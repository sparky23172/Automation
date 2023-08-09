package main

import (
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"io/fs"
	"log"
	"os"
	"os/signal"
	"path/filepath"
	"strconv"
	"time"

	"go.uber.org/zap"
)

var logger *zap.SugaredLogger

type hashez struct {
	Path string `json:"path"`
	Hash string `json:"hash"`
	Time string `json:"time"`
}

func initialization() map[string]string {
	logz, _ := zap.NewDevelopment()

	//logz, _ := zap.NewProduction()
	sugar := logz.Sugar()
	// Change logging to info
	sugar = sugar.WithOptions(zap.IncreaseLevel(zap.InfoLevel))
	logger = sugar

	sugar.Info("Initializing Starting!")

	sugar.Debug("Parsing Arguments")
	dirPtr := flag.String("dir", ".", "Directory you would like scanned. Default is current directory (.)")
	debugPtr := flag.Bool("debug", false, "Turn on Debugging")
	countPtr := flag.Int("count", 3, "Number of times to run. 99 will cause a near infinite counter for longer scan times")
	delayPtr := flag.Int("delay", 5, "Number of seconds to wait in between scans")
	csvPtr := flag.Bool("csv", false, "Turn on CSV output")
	silentPtr := flag.Bool("silent", false, "Make the tool silent")
	// outputPtr := flag.String("output", "tools", "Folder to place output of results")

	flag.Parse()

	sugar.Debug("Checking Arguments")
	dir := *dirPtr
	debug := *debugPtr
	count := *countPtr
	delay := *delayPtr
	csv := *csvPtr
	silent := *silentPtr

	defer sugar.Sync()

	output := make(map[string]string)

	if debug {
		sugar.Info("Debug Mode Enabled")
		sugar = sugar.WithOptions(zap.IncreaseLevel(zap.DebugLevel))
		logger = sugar
	}

	if silent {
		sugar.Info("Silent Mode Enabled")
		sugar = sugar.WithOptions(zap.IncreaseLevel(zap.WarnLevel))
		logger = sugar
	}

	output["dir"] = dir
	output["debug"] = fmt.Sprintf("%t", debug)
	output["count"] = fmt.Sprintf("%d", count)
	output["delay"] = fmt.Sprintf("%d", delay)
	output["csv"] = fmt.Sprintf("%t", csv)

	return output
}

func hash_file_sha1(filePath string) (string, error) {
	var returnSHA1String string
	file, err := os.Open(filePath)
	if err != nil {
		return returnSHA1String, err
	}
	defer file.Close()
	hash := sha1.New()
	if _, err := io.Copy(hash, file); err != nil {
		return returnSHA1String, err
	}
	hashInBytes := hash.Sum(nil)[:20]
	returnSHA1String = hex.EncodeToString(hashInBytes)
	return returnSHA1String, nil
}

func tree(base string, output map[string]string, hashes map[string]string, json map[string]hashez) (map[string]string, map[string]hashez, error) {
	update := false
	now := time.Now()
	logger.Debugf("Now: %s", now.Format("15:04:05 MST (+01) 02/01/06"))
	err := filepath.WalkDir(base, func(path string, d fs.DirEntry, errz error) error {
		if output["debug"] == "true" {
			logger.Debugf("Path - %s; File - %s; %s - %t", path, d.Name(), "directory?", d.IsDir())
		}
		if d.IsDir() {
			return nil
		}
		// fmt.Println(path)
		hash, err := hash_file_sha1(path)

		if hashes[path] != "" {
			if hash != hashes[path] {
				logger.Debugf("Hashes do not match for %s: %s - %s", path, hashes[path], hash)
				update = true
			} else {
				if output["debug"] == "true" {
					logger.Debugf("Hashes match for %s: %s - %s", path, hashes[path], hash)
				}
			}
		}

		if err == nil {
			logger.Debugf("%s - %s", path, hash)
			hashes[path] = hash

			oldPath := path
			if update {
				logger.Info("Updating JSON")
				counter := 0
				// If I see a key of path+counter, then I need to increment counter
				// If I don't see a key of path+counter, then I need to add a key of path+counter
				newPath := path + "_" + strconv.Itoa(counter)
				_, exists := json[newPath]
				logger.Debugf("Exists: %t", exists)
				if !exists {
					path = path + "_" + strconv.Itoa(counter)

				} else {
					for ; exists; counter++ {
						newPath = path + "_" + strconv.Itoa(counter)
						_, exists = json[newPath]
					}
					path = newPath
				}
				update = false
			}

			hashy := hashez{Path: oldPath, Hash: hash, Time: now.Format("15:04:05")}
			_, exists := json[path]
			if !exists {
				json[path] = hashy
			} else {
				logger.Debugf("Path already exists: %s", path)
			}

		} else {
			logger.Error(err)
		}
		logger.Debugf("Hashes: %s", hashes)
		logger.Debugf("JSON: %s", json)
		return nil
	})
	if err != nil {
		log.Fatalf("impossible to walk directories: %s", err)
	}
	logger.Debug("Returning")
	logger.Debugf("Hashes: %s", hashes)
	logger.Debugf("JSON: %s", json)

	return hashes, json, err
}

func main() {
	output := initialization()

	logger.Debugf("Flags: %s", output)
	logger.Debugf("Debug: %s", output["debug"])
	logger.Debugf("Count: %s", output["count"])

	// Change string to int
	count, _ := strconv.Atoi(output["count"])
	delay, _ := strconv.Atoi(output["delay"])
	init := 0

	hashes := make(map[string]string)
	jsonz := make(map[string]hashez)

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	go func() {
		for sig := range c {
			logger.Debugf("Caught: %s. Ending Cycles", sig)
			logger.Infof("Pre  - Count: %d\tInit: %d", count, init)
			init = count
			logger.Infof("Post - Count: %d\tInit: %d", count, init)
		}
	}()

	if output["count"] == "99" {
		init = -999
	}

	for init != count {
		hashesNew, jsonNew, err := tree(output["dir"], output, hashes, jsonz)
		if err != nil {
			logger.Error(err)
		}
		hashes = hashesNew
		jsonz = jsonNew
		init++
		logger.Infof("Sleeping for %d seconds - Count: %d\n\n\n", delay, init)
		time.Sleep(time.Duration(delay) * time.Second)
	}
	bytes, _ := json.Marshal(jsonz)
	if output["csv"] == "true" {
		// Write json to file
		header := "File with iteration,Path to file,Sha1 Hash,Time of original hashing\n"
		for x, y := range jsonz {
			logger.Debugf(x, y)
			header += x + "," + y.Path + "," + y.Hash + "," + y.Time + "\n"
		}
		err := os.WriteFile("output.csv", []byte(header), 0644)
		if err != nil {
			logger.Error(err)
		}

	} else {
		err := os.WriteFile("output.txt", bytes, 0644)
		if err != nil {
			logger.Error(err)
		}
	}
	logger.Info("Done!")
}
