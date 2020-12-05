package main

import (
    "os"
    "fmt"
    "runtime"
    "path/filepath"
    "syscall"
    "encoding/json"
    "strings"
    "os/exec"

    // dirutils
    "os/user"
    "math/rand"
    "time"
)



const dockerhitch = `FROM ubuntu:focal

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install tzdata -y && echo "Europe/London" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

RUN adduser root sudo && apt-get install -y sudo

RUN apt-get update && apt-get upgrade -y && apt-get install \
    python-setuptools build-essential python3-pip \
    virtualenv python3 inetutils-ping git \
    golang-go wget curl libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
    xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev -y



RUN useradd -ms /bin/bash hitch
RUN adduser hitch sudo
RUN echo "hitch ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN mkdir /gen/
RUN mkdir /gen/share
RUN ln -s /gen/share /share
RUN chown hitch:hitch /gen
RUN chown hitch:hitch /share

USER hitch
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

func docker() string {
    return "docker"
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

func realized_hitch_folder(hitchdir string) string {
    folder, err := filepath.EvalSymlinks(hitchdir + "/" + "gen")
    
    if err != nil {
        die("Error getting hitch folder from : " + hitchdir + "/" + "gen")
    }
    
    return folder
}

func is_there_hitch_folder(hitchdir string) bool {
    _, err := filepath.EvalSymlinks(hitchdir + "/" + "gen")
    
    return err != nil
}

func clean(projectpath string) {
    hitchfolder := realized_hitch_folder(projectpath)
    fmt.Println("Cleaning " + hitchfolder)
    if fileExists(hitchfolder + "/" + "Dockerhitch") {
        fmt.Println("Removing docker container...")
        hitchcode := filepath.Base(hitchfolder)
        run_command(docker(), []string{"rmi", "-f", "hitch-" + hitchcode})
        run_command(docker(), []string{"volume", "rm", "-f", "hitchv-" + hitchcode})
    }
    os.RemoveAll(hitchfolder)
    os.Remove(projectpath + "/" + "gen")
    os.Exit(0)
}

func dockerrun(projectdir string, hitchcode string, arguments []string) {
    run_command(
        docker(), 
        append(
            []string{
                "run", "--rm", "-v",
                projectdir + ":/home/hitch/project",
                "--mount",
                "type=volume,source=hitchv-" + hitchcode + ",destination=/gen",
                "hitch-" + hitchcode,
            },
            arguments...
        ),
    )
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
            fmt.Println(hitchdir)
            if is_there_hitch_folder(realized_hitch_folder(hitchdir)) {
                clean(hitchdir)
            } else {
                die("No installed project, nothing to clean.")
            }
        }
    }
    
    if hitchdir == "" {
        die("key.py not found in any directory\n\n" + strings.Join(checked_folders, "\n"))
    } else {
        projectdir := filepath.Dir(hitchdir)

        if !fileExists(hitchdir + "/" + "gen") {
            if len(arguments) == 2 {
                if arguments[1] == "--docker" {
                    genpath := new_hitch_dir()
                    fmt.Println("Creating new hitch folder " + genpath)
                    os.MkdirAll(genpath, os.ModePerm)
                    os.Symlink(genpath, hitchdir + "/" + "gen")
                    hitchcode := filepath.Base(genpath)
                    
                    writefile(genpath + "/" + "Dockerhitch", dockerhitch)
                    run_command(docker(), []string{"build", ".", "-f", genpath + "/" + "Dockerhitch", "-t", "hitch-" + hitchcode})
                    run_command(docker(), []string{"volume", "create", "hitchv-" + hitchcode})
                    dockerrun(projectdir, hitchcode, []string{"virtualenv", "/gen/hvenv", "--python=python3"})
                    dockerrun(projectdir, hitchcode, []string{"/gen/hvenv/bin/pip", "install", "pip==20.2"})
                    dockerrun(projectdir, hitchcode, []string{"/gen/hvenv/bin/pip", "install", "-r", "/home/hitch/project/hitch/hitchreqs.txt"})
                    dockerrun(projectdir, hitchcode, []string{"bash", "-c", "echo /home/hitch/project/hitch > /gen/hvenv/linkfile"})
                } else if arguments[1] == "--folder" {
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
            } else {
                die("key.py found in " + hitchdir + ". Run 'hk --docker' or 'hk --folder' to build")
            }
            
        } else {
            genpath := realized_hitch_folder(hitchdir)
            if fileExists(genpath + "/" + "Dockerhitch") {
                hitchcode := filepath.Base(genpath)

                err := syscall.Exec(
                    "/usr/bin/docker",
                    append(
                        []string{
                            "/usr/bin/docker",
                            "run", "--rm", "-it", "-v",
                            projectdir + ":/home/hitch/project",
                            "--mount",
                            "type=volume,source=hitchv-" + hitchcode + ",destination=/gen",
                            "--workdir", "/home/hitch/project",
                            "hitch-" + hitchcode,
                            "/gen/hvenv/bin/hitchrun",
                        },
                        arguments[1:]...
                    ),
                    os.Environ(),
                )
                fmt.Println(err)
                os.Exit(0)
            } else {
                hitchrun := genpath + "/" + "hvenv" + "/" + "bin" + "/" + "hitchrun"
                syscall.Exec(
                    hitchrun,
                    append([]string{hitchrun}, arguments[1:]...),
                    os.Environ(),
                )
                os.Exit(0)
            }
        }
    }

    
}

func main() {
    if runtime.GOOS == "windows" {
        die("HitchKey does not yet support windows.")
    } else {
        execute()
    }
}

