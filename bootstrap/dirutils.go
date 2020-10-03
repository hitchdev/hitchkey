package main

import (
    "os/user"
    "math/rand"
    "time"
)

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
