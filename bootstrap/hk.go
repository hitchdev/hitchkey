package main

import (
    "os"
    "fmt"
    "runtime"
    "path/filepath"
    "syscall"
    "encoding/json"
    "strings"
)

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
    
    if len(arguments) == 2 {
        if arguments[1] == "--help" {
            fmt.Println("help")
            os.Exit(0)
        }
    }
    
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
        die("key.py not found in any directory\n\n" + strings.Join(checked_folders, "\n"))
    }

    realized_hitch_folder, err := filepath.EvalSymlinks(checkdir + "/" + "gen")
    
    if err != nil {
       die("cannot find gen file in " + checkdir)
    }
    
    hitchrun := realized_hitch_folder + "/" + "hvenv" + "/" + "bin" + "/" + "hitchrun"
    
    syscall.Exec(
        hitchrun,
        append([]string{hitchrun}, arguments[1:]...),
        os.Environ(),
    )
}

func main() {
    if runtime.GOOS == "windows" {
        fmt.Println("HitchKey does not yet support windows.")
    } else {
        execute()
    }
}

