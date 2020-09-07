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
    f, err := os.Create(filename)

    if err != nil {
        die("Error writing file")
    }

    defer f.Close()

    _, err2 := f.WriteString(content)

    if err2 != nil {
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
    info, err := os.Stat(filename)
    if os.IsNotExist(err) {
        return false
    }
    return !info.IsDir()
}

func currentDirectory() string {
    path, err := os.Getwd()
    if err != nil {
        return ""
    }
    return path
}



func execute() {
    arguments := os.Args
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
    
    if len(arguments) == 2 {
        if arguments[1] == "--help" {
            fmt.Println("help")
            os.Exit(0)
        }
        
        if arguments[1] == "--clean" {
            fmt.Println(checkdir)
            realized_hitch_folder2, err2 := filepath.EvalSymlinks(checkdir + "/" + "gen")
            if err2 == nil {
                fmt.Println("Cleaning " + realized_hitch_folder2)
                os.RemoveAll(realized_hitch_folder2)
                os.Remove(checkdir + "/" + "gen")
                os.Exit(0)
            } else {
                die("No installed project, nothing to clean.")
            }
        }
    }
    
    if checkdir == "/" {
        die("key.py not found in any directory\n\n" + strings.Join(checked_folders, "\n"))
    }

    if !fileExists(checkdir + "/" + "gen") {
        genpath := new_hitch_dir()
        fmt.Println("Creating new hitch folder " + genpath)
        os.MkdirAll(genpath, os.ModePerm)
        os.Symlink(genpath, checkdir + "/" + "gen")
        
        run_command(virtualenv(), []string{genpath + "/" + "hvenv", "-p", python3()})
        run_command(
            genpath + "/" + "hvenv" + "/" + "bin" + "/" + "pip",
            []string{"install", "hitchrun"},
        )
        writefile(genpath + "/" + "hvenv" + "/" + "linkfile", checkdir)
    }
    
    realized_hitch_folder, err := filepath.EvalSymlinks(checkdir + "/" + "gen")
    
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

