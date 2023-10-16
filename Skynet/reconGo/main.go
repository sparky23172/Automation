package main

import (
	"bytes"
	"flag"
	"fmt"
	"io/ioutil"
	"net"
	"net/http"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"sync"
	"time"

	"go.uber.org/zap"
)

var PATH = ""
var logger *zap.SugaredLogger

func contains(s []string, str string) bool {
	for _, v := range s {
		if v == str {
			return true
		}
	}

	return false
}

func initialization() (string, map[string]bool) {
	logz, _ := zap.NewDevelopment()
	// logz, _ := zap.NewProduction()

	sugar := logz.Sugar()
	logger = sugar

	sugar.Info("Initializing Starting!")

	sugar.Debug("Parsing Arguments")
	domainPtr := flag.String("domain", "", "Domain you would like scanned")
	debugPtr := flag.Bool("debug", false, "Turn on Debugging")
	activePtr := flag.Bool("active", false, "Turn on Active Recon and disregarding safeguard")
	outputPtr := flag.String("output", "tools", "Folder to place output of results")

	flag.Parse()

	sugar.Debug("Checking Arguments")
	debug := *debugPtr
	domain := *domainPtr
	active := *activePtr
	output := *outputPtr

	sugar.Debugf("Debug: %t", debug)
	sugar.Debugf("Domain: %s", domain)
	sugar.Debugf("Active: %t", active)
	sugar.Debugf("Output Directory: %s", output)

	PATH = output

	if domain == "" {
		sugar.Fatal("No domain provided")
	}

	if domain != "" {
		sugar.Debugf("Domain provided: %s", domain)
		// Do some sanitization
		sugar.Debugf("Doing sanitization on: %s", domain)
		domain = strings.TrimPrefix(domain, "https://") // Remove http:s// from domain
		domain = strings.TrimPrefix(domain, "http://")  // Remove http:// from domain
		if strings.Contains(domain, "/") {              // Remove any trailing paths
			domain = strings.Split(domain, "/")[0]
		}

		sugar.Debugf("Domain provided: %s", domain)
	}

	tools := make(map[string]bool)

	sugar.Debug("Checking to see if nslookup is installed")
	_, _, nslookupState := nslookup("", true)
	sugar.Debug("Checking to see if crt.sh is accessible")
	_, crtShState := crtSh("", true, nil)
	sugar.Debug("Checking to see if amass is installed")
	_, _, amassState := amass("", nil, nil, true, nil)
	sugar.Debug("Checking to see if shodan is installed")
	shodanState := shodan("", nil, nil, true, nil)
	sugar.Debug("Checking to see if Http Obs is installed")
	httpObsState := httpObs("", true, nil)
	sugar.Debug("Checking to see if sslscan is installed")
	sslScanState := sslscan("", true, nil)
	sugar.Debug("Checking to see if testSSL is installed")
	testsslState := testSSL("", true, nil)
	sugar.Debug("Checking to see if wafw00f is installed")
	wafw00fState := wafw00f("", true, nil)
	sugar.Debug("Checking to see if whatweb is installed")
	whatwebState := whatweb("", true, nil)
	sugar.Debug("Checking to see if wayback is installed")
	waybackState := wayback("", true, nil)

	tools["nslookup"] = nslookupState
	tools["crtSh"] = crtShState
	tools["amass"] = amassState
	tools["shodan"] = shodanState
	tools["httpObs"] = httpObsState
	tools["sslScan"] = sslScanState
	tools["testssl"] = testsslState
	tools["wafw00f"] = wafw00fState
	tools["wayback"] = waybackState
	tools["whatweb"] = whatwebState

	sugar.Info("Initializing Complete!")

	defer sugar.Sync()

	return domain, tools
}

func saveOutput(output string, filename string, command []string, now time.Time) {

	_, err := os.Stat(PATH)
	if os.IsNotExist(err) {
		logger.Error("Folder does not exist. Making directory")
		os.Mkdir(PATH, 0755)
	}

	logger.Debugf("Command ran: %s", strings.Join(command, " "))
	logger.Debugf("Time Command ran: %s", now.Format("15:04:05 MST (+01) 02/01/06"))

	text := []byte("Time command was ran: " + now.Format("15:04:05 MST (+01) 02/01/06") + "\n" + "Command Ran: " + strings.Join(command, " ") + "\n\nOutput:\n" + output)

	err = os.WriteFile(PATH+"/"+filename, text, 0644)
	if err != nil {
		logger.Error(err)
	}
}

func whatweb(domain string, statusCheck bool, waitgroup *sync.WaitGroup) bool {
	if statusCheck {
		command := make([]string, 2)
		command[0] = "whatweb"
		command[1] = "--version"

		cmd := exec.Command(command[0], command[1])
		var out bytes.Buffer
		cmd.Stdout = &out
		err := cmd.Run()
		logger.Debugf("%s\n", out.String())
		if err != nil {
			logger.Error("Error: ", err)
			return false
		}
		return true
	}
	command := make([]string, 5)
	command[0] = "whatweb"
	command[1] = "-a3"
	command[2] = domain
	command[3] = "-v"
	command[4] = "--color=never"

	now := time.Now()
	logger.Debugf("Command ran: %s", strings.Join(command, " "))
	cmd := exec.Command(command[0], command[1], command[2], command[3], command[4])
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	output := out.String()
	logger.Debugf("%s\n", output)
	if err != nil {
		logger.Error("Error: ", err)
		return false
	}
	saveOutput(output, "whatweb.txt", command, now)
	waitgroup.Done()
	return true

}

func wayback(domain string, statusCheck bool, waitgroup *sync.WaitGroup) bool {
	home, err := os.UserHomeDir()
	if err != nil {
		logger.Error(err)
	}
	if statusCheck {
		command := make([]string, 2)
		command[0] = "/" + home + "/tools/waybackurls/waybackurls"
		command[1] = "-h"

		cmd := exec.Command(command[0], command[1])
		var out bytes.Buffer
		cmd.Stdout = &out
		err := cmd.Run()
		logger.Debugf("%s\n", out.String())
		if err != nil {
			logger.Error("Error: ", err)
			return false
		}
		return true
	}
	command := make([]string, 3)
	command[0] = home + "/tools/waybackurls/waybackurls"
	command[1] = "-dates"
	command[2] = domain

	now := time.Now()
	logger.Debugf("Command ran: %s", strings.Join(command, " "))
	cmd := exec.Command(command[0], command[1], command[2])
	var out bytes.Buffer
	cmd.Stdout = &out
	err = cmd.Run()
	output := out.String()
	// logger.Debugf("%s\n", output)
	if err != nil {
		logger.Error("Error: ", err)
		return false
	}
	saveOutput(output, "waybackurls.txt", command, now)
	waitgroup.Done()
	return true

}

func sslscan(domain string, statusCheck bool, waitgroup *sync.WaitGroup) bool {
	if statusCheck {
		command := make([]string, 3)
		command[0] = "sslscan"
		command[1] = "--version"
		command[2] = "--no-color"

		cmd := exec.Command(command[0], command[1], command[2])
		var out bytes.Buffer
		cmd.Stdout = &out
		err := cmd.Run()
		logger.Debugf("%s\n", out.String())
		if err != nil {
			logger.Error("Error: ", err)
			return false
		}
		return true
	}
	command := make([]string, 3)
	command[0] = "sslscan"
	command[1] = "--no-color"
	command[2] = domain

	now := time.Now()
	logger.Debugf("Command ran: %s", strings.Join(command, " "))
	cmd := exec.Command(command[0], command[1], command[2])
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	output := out.String()
	logger.Debugf("%s\n", output)
	if err != nil {
		logger.Error("Error: ", err)
		return false
	}
	saveOutput(output, "sslscan.txt", command, now)
	waitgroup.Done()
	return true

}

func testSSL(domain string, statusCheck bool, waitgroup *sync.WaitGroup) bool {
	home, err := os.UserHomeDir()
	if err != nil {
		logger.Error(err)
	}
	if statusCheck {
		command := make([]string, 3)
		command[0] = "bash"
		command[1] = home + "/tools/testssl/testssl.sh"
		command[2] = "--version"

		cmd := exec.Command(command[0], command[1], command[2])
		var out bytes.Buffer
		var out2 bytes.Buffer
		cmd.Stdout = &out
		cmd.Stderr = &out2
		err := cmd.Run()
		logger.Debugf("%s\n", out.String())
		if err != nil {
			logger.Debugf("%s\n", out2.String())
			logger.Error("Error: ", err)
			return false
		}
		return true
	}
	command := make([]string, 4)
	command[0] = "bash"
	command[1] = home + "/tools/testssl/testssl.sh"
	command[2] = "--color=0"
	command[3] = domain

	now := time.Now()
	logger.Debugf("Command ran: %s", strings.Join(command, " "))
	cmd := exec.Command(command[0], command[1], command[2], command[3])
	var out bytes.Buffer
	cmd.Stdout = &out
	err = cmd.Run()
	output := out.String()
	logger.Debugf("%s\n", output)
	if err != nil {
		logger.Error("Error: ", err)
		return false
	}
	saveOutput(output, "TestSSL.txt", command, now)
	waitgroup.Done()
	return true

}

func wafw00f(domain string, statusCheck bool, waitgroup *sync.WaitGroup) bool {
	if statusCheck {
		command := make([]string, 2)
		command[0] = "wafw00f"
		command[1] = "--version"

		cmd := exec.Command(command[0], command[1])
		var out bytes.Buffer
		cmd.Stdout = &out
		err := cmd.Run()
		logger.Debugf("%s\n", out.String())
		if err != nil {
			logger.Error("Error: ", err)
			return false
		}
		return true
	}
	command := make([]string, 4)
	command[0] = "wafw00f"
	command[1] = "-vv"
	command[2] = "-a"
	command[3] = domain

	now := time.Now()
	logger.Debugf("Command ran: %s", strings.Join(command, " "))
	cmd := exec.Command(command[0], command[1], command[2], command[3])
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	output := out.String()
	logger.Debugf("%s\n", output)
	if err != nil {
		logger.Error("Error: ", err)
		return false
	}
	saveOutput(output, "wafw00f.txt", command, now)
	waitgroup.Done()
	return true

}

func httpObs(domain string, statusCheck bool, waitgroup *sync.WaitGroup) bool {
	home, err := os.UserHomeDir()
	if err != nil {
		logger.Error(err)
	}
	if statusCheck {
		command := make([]string, 3)
		command[0] = "/usr/bin/python3"
		command[1] = home + "/tools/http-observatory/httpobs-local-scan"
		command[2] = "-h"

		cmd := exec.Command(command[0], command[1], command[2])
		var out bytes.Buffer
		cmd.Stdout = &out
		err := cmd.Run()
		logger.Debugf("%s\n", out.String())
		if err != nil {
			logger.Error("Error: ", err)
			return false
		}
		return true
	}
	command := make([]string, 5)
	command[0] = "/usr/bin/python3"
	command[1] = home + "/tools/http-observatory/httpobs-local-scan"
	command[2] = domain
	command[3] = "--format"
	command[4] = "report"

	now := time.Now()
	logger.Debugf("Command ran: %s", strings.Join(command, " "))
	cmd := exec.Command(command[0], command[1], command[2])
	var out bytes.Buffer
	cmd.Stderr = &out
	err = cmd.Run()
	output := out.String()

	fmt.Printf("Out: %s\n", output)
	if err != nil {
		logger.Error("Error: ", err)
		return false
	}
	saveOutput(string(output), "http-observatory.txt", command, now)
	waitgroup.Done()
	return true

}

func nslookup(domain string, statusCheck bool) (string, []string, bool) {

	if statusCheck {
		_, err := exec.Command("nslookup", "-version").Output()
		if err != nil {
			logger.Errorf("%s", err)
			return "", nil, false
		}
		return "", nil, true
	}

	logger.Infof("Preforming nslookup on %s", domain)
	command := make([]string, 2)
	command[0] = "nslookup"
	command[1] = domain

	nslookupRecords := make([]string, 6)
	nslookupRecords[0] = "-query=A"
	nslookupRecords[1] = "-query=PTR"
	nslookupRecords[2] = "-query=ANY"
	nslookupRecords[3] = "-query=TXT"
	nslookupRecords[4] = "-query=MX"
	nslookupRecords[5] = "-query=NS"

	now := time.Now()
	out, err := exec.Command(command[0], command[1]).Output()
	// Output handling
	if err != nil {
		logger.Errorf("%s", err)
		if strings.Contains(err.Error(), "exit status 1") {
			logger.Error("Issue with running nslookup...")
			saveOutput("exit status 1", "nslookup.txt", command, now)
			return "", nil, false
		}
		return "", nil, false
	} else {
		logger.Debug("Command Successfully Executed")
		output := string(out[:])
		logger.Info(output)

		saveOutput(output, "nslookup.txt", command, now)

		// Grab IP address(es) from nslookup
		logger.Debug("Grabbing IP address(es) from nslookup")
		re := regexp.MustCompile(`(?m)(?:Address: )(.*)`)
		ipz := re.FindAllStringSubmatch(output, -1)
		logger.Debug("IP results: %s", ipz)

		var ips []string

		if len(ipz) > 1 {
			logger.Info("Multiple IP addresses found")

			for _, ip := range ipz {
				if !strings.Contains(ip[1], ":") {
					logger.Debugf("Found IP Address: %s", ip[1])
					ips = append(ips, string(ip[1]))
				} else {
					logger.Debugf("Skipping adding IPv6 Address: %s", ip[1])
				}
			}
		} else {
			ips = append(ips, string(ipz[0][1]))
		}
		logger.Infof("IP Address(es) 1: %s", ips)
		logger.Debugf("Length of IP Address(es): %d", len(ips))

		for i := 0; i != len(nslookupRecords); i++ {
			tmpCommand := make([]string, 3)
			tmpCommand[0] = command[0]
			tmpCommand[1] = nslookupRecords[i]
			tmpCommand[2] = command[1]

			now = time.Now()
			out, err = exec.Command(tmpCommand[0], tmpCommand[1], tmpCommand[2]).Output()
			// Output handling
			if err != nil {
				logger.Errorf("%s", err)
				if strings.Contains(err.Error(), "exit status 1") {
					logger.Error("Issue with running nslookup...")
				}
				saveOutput("exit status 1", "nslookup_"+strings.Replace(nslookupRecords[i], "=", "-", -1)+".txt", tmpCommand, now)
			} else {
				logger.Debug("Command Successfully Executed")
				output := string(out[:])
				logger.Info(output)

				saveOutput(output, "nslookup_"+strings.Replace(nslookupRecords[i], "=", "-", -1)+".txt", tmpCommand, now)
			}

		}
		// fmt.Printf("%s", output)
		return domain, ips, true
	}
}

func crtSh(domain string, statusCheck bool, waitgroup *sync.WaitGroup) ([]string, bool) {

	var netTransport = &http.Transport{
		Dial: (&net.Dialer{
			Timeout: 5 * time.Second,
		}).Dial,
		TLSHandshakeTimeout: 5 * time.Second,
	}
	var netClient = &http.Client{
		Timeout:   time.Second * 5,
		Transport: netTransport,
	}

	sliceUrls := make([]string, 3)
	sliceUrls[0] = "curl"
	sliceUrls[1] = "https://www.crt.sh/"
	sliceUrls[2] = ` | jq -r '.[] | "\(.name_value)\n\(.common_name)"' | sort -u`

	if statusCheck {
		// resp, err := netClient.Get("http://127.0.0.1:4444/")
		now := time.Now()
		resp, err := netClient.Get("https://www.crt.sh/")
		if err != nil {
			logger.Warnf("An Error has Occured: %s", err.Error())
			saveOutput(err.Error(), "certsh.txt", sliceUrls, now)
			return nil, false
		}

		logger.Debug("Response had no errors")
		if resp != nil {
			logger.Debug("Response had content")
			body, err := ioutil.ReadAll(resp.Body)
			defer resp.Body.Close()
			if err != nil {
				logger.Warnf("An Error has Occured: %s", err.Error())
				saveOutput(err.Error(), "certsh.txt", sliceUrls, now)
				return nil, false
			}
			//Convert the body to type string
			sb := string(body)
			logger.Debugf("Output: %s", sb)
		}
		return nil, true
	}
	now := time.Now()
	url := fmt.Sprintf("https://crt.sh/?q=%s&output=json", domain)

	sliceUrls[1] = url

	resp, err := netClient.Get(url)
	if err != nil {
		logger.Errorf("%s", err)
		saveOutput(err.Error(), "certsh.txt", sliceUrls, now)
		return nil, false
	}
	logger.Debug(resp)

	body, err := ioutil.ReadAll(resp.Body)
	defer resp.Body.Close()
	if err != nil {
		logger.Warnf("An Error has Occured: %s", err.Error())
		saveOutput(err.Error(), "certsh.txt", sliceUrls, now)
		return nil, false
	}
	//Convert the body to type string
	sb := string(body)
	logger.Debugf("Output: %s", sb)

	var urls []string
	re := regexp.MustCompile(`common_name":\"(.+?)\"`)
	ipz := re.FindAllStringSubmatch(sb, -1)
	logger.Debug(ipz)

	for _, y := range ipz {
		logger.Debugf("%s", y[1])
		if !contains(urls, y[1]) {
			urls = append(urls, y[1])
		}
	}

	logger.Debugf("Unique Urls: %s", urls)
	saveOutput(err.Error(), "certsh.txt", sliceUrls, now)
	waitgroup.Done()
	return urls, true

}

func amass(domain string, ips []string, subdomains []string, statusCheck bool, waitgroup *sync.WaitGroup) ([]string, []string, bool) {
	logger.Debug("Work in Progress")
	return nil, nil, true
}

func shodan(domain string, ips []string, subdomains []string, statusCheck bool, waitgroup *sync.WaitGroup) bool {
	if statusCheck {
		command := make([]string, 2)
		command[0] = "shodan"
		command[1] = "version"

		cmd := exec.Command(command[0], command[1])
		var out bytes.Buffer
		cmd.Stdout = &out
		err := cmd.Run()
		logger.Debugf("%s\n", out.String())
		if err != nil {
			logger.Error("Error: ", err)
			return false
		}
		return true
	}

	command := make([]string, 8)
	command[0] = "shodan"
	command[1] = "search"
	command[2] = domain
	command[3] = "--no-color"
	command[4] = "--fields"
	command[5] = "hostnames,net,port"
	command[6] = "--separator"
	command[7] = ","

	now := time.Now()
	logger.Debugf("Command ran: %s", strings.Join(command, " "))
	cmd := exec.Command(command[0], command[1], command[2])
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	output := out.String()
	logger.Debugf("%s\n", output)
	if err != nil {
		logger.Error("Error: ", err)
		return false
	}
	saveOutput(output, "shodan_"+domain+".txt", command, now)

	for _, ip := range ips {
		command := make([]string, 4)
		command[0] = "shodan"
		command[1] = "host"
		command[2] = ip
		command[3] = "--no-color"

		now := time.Now()
		logger.Debugf("Command ran: %s", strings.Join(command, " "))
		cmd := exec.Command(command[0], command[1], command[2])
		var out bytes.Buffer
		cmd.Stdout = &out
		err := cmd.Run()
		output := out.String()
		logger.Debugf("%s\n", output)
		if err != nil {
			logger.Error("Error: ", err)
			return false
		}
		saveOutput(output, "shodan_"+ip+".txt", command, now)
	}

	for _, sub := range subdomains {
		command := make([]string, 8)
		command[0] = "shodan"
		command[1] = "search"
		command[2] = sub
		command[3] = "--no-color"
		command[4] = "--fields"
		command[5] = "hostnames,net,port"
		command[6] = "--separator"
		command[7] = ","

		now := time.Now()
		logger.Debugf("Command ran: %s", strings.Join(command, " "))
		cmd := exec.Command(command[0], command[1], command[2])
		var out bytes.Buffer
		cmd.Stdout = &out
		err := cmd.Run()
		output := out.String()
		logger.Debugf("%s\n", output)
		if err != nil {
			logger.Error("Error: ", err)
			return false
		}
		saveOutput(output, "shodan_"+sub+".txt", command, now)
	}
	waitgroup.Done()
	return true

}

func recon(domain string, tools map[string]bool) {

	// Check if routable
	// Grab IP address(es)
	// Check DNS records
	// Check SSL information for domain similarities
	// Check information on Shodan
	// Check wayback for other versions
	// WAF check
	// Whatweb Check
	// Low LoE host check

	logger.Infof("Recons to preform: %t", tools)

	var ips []string
	var subdomains []string

	wg := new(sync.WaitGroup)

	if tools["nslookup"] {
		logger.Debugf("Running nslookup")
		_, ips, _ = nslookup(domain, false)
		logger.Debugf("IP Addresses Returned: %s", ips)
	}

	if tools["crtSh"] {
		wg.Add(1)
		logger.Debugf("Running crt.sh")
		subdomains, _ = crtSh(domain, false, wg)
		logger.Debugf("Subdomains Returned: %s", subdomains)
	}

	if tools["amass"] {
		// wg.Add(1)
		logger.Debugf("Running Amass")
		subResults, ipResults, _ := amass(domain, ips, subdomains, false, wg)
		logger.Debugf("Subdomains Returned: %s", subResults)
		for _, sub := range subResults {
			if !contains(subdomains, sub) {
				subdomains = append(subdomains, sub)
			}
		}
		for _, ip := range ipResults {
			if !contains(ips, ip) {
				subdomains = append(ips, ip)
			}
		}
		logger.Debugf("amass Returned Successfully")
	}

	if tools["httpObs"] {
		wg.Add(1)
		logger.Debugf("Running Http Obs")
		go httpObs(domain, false, wg)
		logger.Debugf("Http Obs Returned Successfully")
	}

	if tools["sslScan"] {
		wg.Add(1)
		logger.Debugf("Running SSL Scan")
		go sslscan(domain, false, wg)
		logger.Debugf("SSL Scan Returned Successfully")
	}

	if tools["testssl"] {
		wg.Add(1)
		logger.Debugf("Running TestSSL")
		go testSSL(domain, false, wg)
		logger.Debugf("TestSSL Returned Successfully")
	}

	if tools["shodan"] {
		wg.Add(1)
		logger.Debugf("Running Shodan")
		go shodan(domain, ips, subdomains, false, wg)
		logger.Debugf("Shodan Returned Successfully")
	}

	if tools["wafw00f"] {
		wg.Add(1)
		logger.Debugf("Running WAFW00F")
		go wafw00f(domain, false, wg)

		logger.Debugf("WAFW00F Returned Successfully")
	}

	if tools["wayback"] {
		wg.Add(1)
		logger.Debugf("Running Wayback")
		go wayback(domain, false, wg)
		logger.Debugf("Wayback Returned Successfully")
	}

	if tools["whatweb"] {
		wg.Add(1)
		logger.Debugf("Running Whatweb")
		go whatweb(domain, false, wg)
		logger.Debugf("Whatweb Returned Successfully")
	}
	wg.Wait()
	logger.Debugf("ips: %s, subdomains: %s", ips, subdomains)

	logger.Info("Recon Complete")
}

func main() {
	stringz, tools := initialization()
	recon(stringz, tools)
	logger.Info("[+] Go Go Gadget Recon has finished running")
}
