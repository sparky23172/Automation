package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"os/user"

	"github.com/slack-go/slack"
	"go.uber.org/zap"
)

type IP struct {
	Query string
}

var logger *zap.Logger

// Initializes everything
func inital() (string, string, string) {
	logger, _ = zap.NewProduction()
	defer logger.Sync()

	logger.Debug("Reading command line arguments")

	// Grab the command line arguments
	token := flag.String("t", "", "Slack Oauth Token")
	channel := flag.String("c", "", "Slack Channel ID")
	message := flag.String("m", "What's up dog", "Slack Message")
	logLevel := flag.String("l", "info", "Log Level")

	flag.Parse()

	// Set the log level
	switch *logLevel {
	case "debug":
		log.SetFlags(log.LstdFlags | log.Lshortfile)
		logger.Debug("Log level set to debug")
	case "info":
		log.SetFlags(log.LstdFlags)
		logger.Debug("Log level set to info")
	case "warn":
		log.SetFlags(log.LstdFlags)
		logger.Debug("Log level set to warn")
	case "error":
		log.SetFlags(log.LstdFlags)
		logger.Debug("Log level set to error")
	case "fatal":
		log.SetFlags(log.LstdFlags)
		logger.Debug("Log level set to fatal")
	default:
		log.SetFlags(log.LstdFlags)
		logger.Debug("Log level set to info")
	}

	return *token, *channel, *message
}

// Get internal IP for machine
func GetOutboundIP() string {
	conn, err := net.Dial("udp", "8.8.8.8:80")
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	localAddr := conn.LocalAddr().(*net.UDPAddr)
	return localAddr.IP.String()
}

// Where am I?
func getip2() string {
	req, err := http.Get("http://ip-api.com/json/")
	if err != nil {
		return err.Error()
	}
	defer req.Body.Close()

	body, err := ioutil.ReadAll(req.Body)
	if err != nil {
		return err.Error()
	}

	logger.Info(string(body))
	var ip IP
	json.Unmarshal(body, &ip)
	return ip.Query
}

// Main function
func main() {
	// Starting the logger
	token, channel, message := inital()
	logger, err := zap.NewProduction()
	if err != nil {
		panic(err)
	}
	defer logger.Sync()

	// Starting the bot
	logger.Debug("Starting slack bot")

	// Initialize slack client
	api := slack.New(token)

	user, err := user.Current()
	if err != nil {
		logger.Error("Error getting current user", zap.Error(err))
	}
	me := user.Username

	var ret_ip string

	if message == "What's up dog" {
		// Report the IP I am at since I didn't include a message in the argument (Potential security issue detection)
		ret_ip = getip2()
	} else {
		// Report the internal IP since I sent a message in the argument
		ret_ip = GetOutboundIP()
	}

	whoami := fmt.Sprintf(`{"Reporter": "%s", "WhereAmI":"%s"},{"Message":"%s"}`, me, ret_ip, message)

	logger.Info(whoami)

	// Message format
	channelId, _, err := api.PostMessage(
		channel,
		slack.MsgOptionText(whoami, false),
	)

	// Error Checking
	if err != nil {
		panic(err)
	}

	// Success Log
	logger.Debug("Sent Successfully", zap.String("Message", message), zap.String("Channel", channelId))
}
