package main

import (
    "os"
    "fmt"
    "runtime"
    "io/ioutil"
    "path/filepath"
    "syscall"
    "encoding/json"
    "strings"
    "os/exec"
    "flag"

    // dirutils
    "os/user"
    "math/rand"
    "time"
)



const dockerhitch1 = `FROM ubuntu:focal

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install tzdata -y && echo "Europe/London" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

RUN adduser root sudo && apt-get install -y sudo

RUN apt-get update && apt-get upgrade -y && apt-get install \
    python-setuptools build-essential python3-pip \
    virtualenv python3 inetutils-ping git \
    wget curl libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
    xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev -y

ENV PIP_CERT=/etc/ssl/certs/

`

const dockerhitch2 = `


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


func readfile_or_empty(filename string) string {
    if fileExists(filename) {
        data, err := ioutil.ReadFile(filename)
        if err != nil {
            die("Error reading file: " + filename)
        }
        return string(data)
    } else {
        return ""
    }
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
        die("Error running command: " + command + " " + strings.Join(arguments, " "))
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

func whichdocker() string {
    if runtime.GOOS == "windows" {
        return "docker"
    } else {
        output, err := exec.Command("which", "docker").Output()
        
        if err != nil {
            die("Error calling 'which docker' to try and get the docker location.")
        }
        
        return strings.TrimSuffix(string(output), "\n")
    }
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

func mountdir(projectdir string, override_mountdir string) string {
    chosendir := projectdir
    
    if override_mountdir != "" {
        chosendir = override_mountdir
    }
    
    return chosendir
}

func dockerrun(projectdir string, override_mountdir string, hitchcode string, arguments []string) {
    run_command(
        docker(), 
        append(
            []string{
                "run", "--rm", "-v",
                mountdir(projectdir, override_mountdir) + ":/home/hitch/project",
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
        
        use_docker := flag.Bool("docker", false, "build docker environment")
        use_folder := flag.Bool("folder", false, "build folder environment")
        noninteractive := flag.Bool("noninteractive", false, "set up a non-interactive environment")
        mountdirectory := flag.String("mountdir", "", "docker mount directory")
        flag.Parse()
        
        // Anything that starts with hk -- will pass through here...
        if len(arguments) > 1 && strings.HasPrefix(arguments[1], "--") {            
            if *use_docker {
                if !fileExists(hitchdir + "/" + "gen") {
                    genpath := new_hitch_dir()
                    fmt.Println("Creating new hitch folder " + genpath)
                    os.MkdirAll(genpath, os.ModePerm)
                    os.Symlink(genpath, hitchdir + "/" + "gen")
                    hitchcode := filepath.Base(genpath)
                    
                    asroot := readfile_or_empty(hitchdir + "/" + "asroot.sh")
                    
                    if asroot == "" {
                        dockercontents := dockerhitch1 + dockerhitch2
                        writefile(genpath + "/" + "Dockerhitch", dockercontents)
                    } else {
                        dockercontents := dockerhitch1 + "\n\nCOPY asroot.sh /\nRUN chmod +x /asroot.sh\nRUN ./asroot.sh\n\n" + dockerhitch2
                        writefile(genpath + "/" + "asroot.sh", asroot)
                        writefile(genpath + "/" + "Dockerhitch", dockercontents)
                    }
                    
                    if *noninteractive {
                        writefile(genpath + "/" + "noninteractive", "yes")
                    }
                    
                    if *mountdirectory != "" {
                        writefile(genpath + "/" + "mountdirectory", *mountdirectory)
                    }
                    
                    override_mountdir := *mountdirectory
                    
    //                     writefile(genpath + "/" + "Dockerhitch", dockerhitch1 + asroot + dockerhitch2)
                    run_command(docker(), []string{"build", genpath, "-f", genpath + "/" + "Dockerhitch", "-t", "hitch-" + hitchcode})
                    run_command(docker(), []string{"volume", "create", "hitchv-" + hitchcode})
                    dockerrun(projectdir, override_mountdir, hitchcode, []string{"virtualenv", "/gen/hvenv", "--python=python3"})
                    dockerrun(projectdir, override_mountdir, hitchcode, []string{"/gen/hvenv/bin/pip", "install", "pip==20.2"})
                    dockerrun(projectdir, override_mountdir, hitchcode, []string{"/gen/hvenv/bin/pip", "install", "-r", "/home/hitch/project/hitch/hitchreqs.txt"})
                    dockerrun(projectdir, override_mountdir, hitchcode, []string{"bash", "-c", "echo /home/hitch/project/hitch > /gen/hvenv/linkfile"})
                    os.Exit(0)
                }
            } else if *use_folder {
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
                    os.Exit(0)
                }
            }
        }
            
        genpath := realized_hitch_folder(hitchdir)
        if fileExists(genpath + "/" + "Dockerhitch") {
            hitchcode := filepath.Base(genpath)
            
            docker_interactive_args := []string{"run", "--rm",}

            if !fileExists(genpath + "/" + "noninteractive") {
                docker_interactive_args = []string{"run", "--rm", "-it",}
            }
            
            mount_directory := ""
            
            if fileExists(genpath + "/" + "mountdirectory") {
                mount_directory = readfile_or_empty(genpath + "/" + "mountdirectory")
            }

            docker_arguments := append(
                docker_interactive_args, 
                []string{
                    "-v",
                    mountdir(projectdir, mount_directory) + ":/home/hitch/project",
                    "--network", "host",
                    "--mount",
                    "type=volume,source=hitchv-" + hitchcode + ",destination=/gen",
                    "--workdir", "/home/hitch/project",
                    "hitch-" + hitchcode,
                    "/gen/hvenv/bin/hitchrun",
                }...,
            )
            
            docker_arguments = append(
                docker_arguments,
                arguments[1:]...
            )
            
            writefile(genpath + "/" + "lastcommand", strings.Join(docker_arguments, " "))

            dockercmd := whichdocker()

            if runtime.GOOS == "windows" {
                cmd := exec.Command(dockercmd, docker_arguments...)
                cmd.Stdout = os.Stdout
                cmd.Stdin = os.Stdin
                cmd.Stderr = os.Stderr
                out_err := cmd.Run()
                fmt.Println(out_err)
            } else {
                out_err := syscall.Exec(
                    dockercmd,
                    append([]string{dockercmd}, docker_arguments...),
                    os.Environ(),
                )
                if out_err != nil {
                    os.Exit(1)
                } else {
                    os.Exit(0)
                }
            }
            
            os.Exit(0)
        } else {
            hitchrun := genpath + "/" + "hvenv" + "/" + "bin" + "/" + "hitchrun"
            syscall.Exec(
                hitchrun,
                append([]string{hitchrun}, arguments[1:]...),
                os.Environ(),
            )
        }
    }
}

func main() {
    execute()
}

