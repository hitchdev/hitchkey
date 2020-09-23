package main

import (
    "os"
    "fmt"
    "runtime"
    "path/filepath"
    "syscall"
    "encoding/json"
    "strings"
    "os/user"
    "os/exec"
    "math/rand"
    "time"
)

const dockerhitch = `FROM ubuntu:focal

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install tzdata -y

RUN echo "Europe/London" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

RUN adduser root sudo && apt-get install -y sudo

RUN apt-get update && apt-get upgrade -y

RUN apt-get install \
    python-setuptools build-essential python3-pip \
    virtualenv python3 inetutils-ping git \
    golang-go -y

RUN useradd -ms /bin/bash hitch
RUN adduser hitch sudo
RUN echo "hitch ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER hitch
RUN mkdir /home/hitch/gen
WORKDIR /home/hitch/
`

const charset = "abcdefghijklmnopqrstuvwxyz1234567890"

func new_hitch_dir() string {
    user, err := user.Current()
    if err != nil {
        die("error getting home directory")
    }
    
    var seededRand *rand.Rand = rand.New(rand.NewSource(time.Now().UnixNano()))

    folder := make([]byte, 6)
    for i := range folder {
        folder[i] = charset[seededRand.Intn(len(charset))]
    }

    return user.HomeDir + "/" + ".hitch" + "/" + string(folder)
}


func writefile(filename string, content string) {
    filehandle, create_err := os.Create(filename)

    if create_err != nil {
        die("Error creating file")
    }

    defer filehandle.Close()

    _, write_err := filehandle.WriteString(content)

    if write_err != nil {
        die("Error writing file")
    }
}

func run_command(command string, arguments []string) {
    cmd := exec.Command(command, arguments...)
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr
    err := cmd.Run()
    if err != nil {
        die("Error running command")
    }
}

func virtualenv() string {
    return "virtualenv"
}

func python3() string {
    return "python3"
}

func prettyPrint(i interface{}) string {
    s, _ := json.MarshalIndent(i, "", "\t")
    return string(s)
}

func die(message string) {
    fmt.Println(message)
    os.Exit(1)
}

func fileExists(filename string) bool {
    _, err := os.Stat(filename)
    if os.IsNotExist(err) {
        return false
    }
    return true
}

func currentDirectory() string {
    path, err := os.Getwd()
    if err != nil {
        die("Error getting current directory")
    }
    return path
}


func get_hitch_dir() (string, []string) {
checkdir := currentDirectory()
    hitchfolder_path := ""
    
    var checked_folders []string
    
    for checkdir != "/" {
        hitchfolder_path = checkdir + "/" + "hitch"
        
        checked_folders = append(checked_folders, checkdir)
        
        if fileExists(checkdir + "/" + "key.py") {
            break
        }
        
        checked_folders = append(checked_folders, hitchfolder_path)
        if fileExists(hitchfolder_path + "/" + "key.py") {
            checkdir = hitchfolder_path
            break
        }
        
        checkdir = filepath.Dir(checkdir)
    }
    
    if checkdir == "/" {
        return "", checked_folders
    } else {
        return checkdir, checked_folders
    }
}



func execute() {
    arguments := os.Args
    
    hitchdir, checked_folders := get_hitch_dir()

    
    if len(arguments) == 2 {
        if arguments[1] == "--help" {
            fmt.Println("help")
            os.Exit(0)
        }
        
        if arguments[1] == "--clean" {
            realized_hitch_folder, err := filepath.EvalSymlinks(hitchdir + "/" + "gen")
            if err == nil {
                fmt.Println("Cleaning " + realized_hitch_folder)
                os.RemoveAll(realized_hitch_folder)
                os.Remove(hitchdir + "/" + "gen")
                os.Exit(0)
            } else {
                die("No installed project, nothing to clean.")
            }
        }
    }
    
    if hitchdir == "" {
        die("key.py not found in any directory\n\n" + strings.Join(checked_folders, "\n"))
    }

    if !fileExists(hitchdir + "/" + "gen") {
        genpath := new_hitch_dir()
        fmt.Println("Creating new hitch folder " + genpath)
        os.MkdirAll(genpath, os.ModePerm)
        os.Symlink(genpath, hitchdir + "/" + "gen")
        
        run_command(virtualenv(), []string{genpath + "/" + "hvenv", "-p", python3()})
        run_command(
            genpath + "/" + "hvenv" + "/" + "bin" + "/" + "pip",
            []string{"install", "hitchrun"},
        )
        writefile(genpath + "/" + "hvenv" + "/" + "linkfile", hitchdir)
    }
    
    realized_hitch_folder, err := filepath.EvalSymlinks(hitchdir + "/" + "gen")
    
    if err != nil {
        die("gen file screw up")
    }
       
    hitchrun := realized_hitch_folder + "/" + "hvenv" + "/" + "bin" + "/" + "hitchrun"
    
    syscall.Exec(
        hitchrun,
        append([]string{hitchrun}, arguments[1:]...),
        os.Environ(),
    )
    os.Exit(0)
}

func main() {
    if runtime.GOOS == "windows" {
        fmt.Println("HitchKey does not yet support windows.")
    } else {
        execute()
    }
}

