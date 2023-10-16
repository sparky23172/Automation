# ReconGo

This program is designed for running in Kali Linux (Debian x86_64). 
Table below explains requirements needed for program to run optimally


| Program         | Additional Information                                                                                                | Requirements                |
| --------------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| nslookup        | Not concurrent                                                                                                        | Just needs to be in path    |
| crtSh           | Needs jq also to be installed                                                                                         | Needs curl and jq           |
| amass           | Not currently deployed                                                                                                | Nothing                     |
| shodan          | Needs an API key for functionality                                                                                    | Needs API key               |
| httpObservatory | Needs to be downloaded, put in ~/tools/http-observatory/ , needs https-local-scan to be copied to it's home directory | Download and put in ~/tools |
| sslScan         | Nothing special outside of installed                                                                                  | Just needs to be in path    |
| testssl         | Needs to be downloaded, put in ~/tools/testssl/                                                                       | Download and put in ~/tools |
| wafw00f         | Nothing special outside of installed                                                                                  | Just needs to be in path    |
| wayback         | Needs to be downloaded, put in ~/tools/waybackurls/                                                                   | Download and put in ~/tools |
| whatweb         | Nothing special outside of installed                                                                                  | Just needs to be in path    |

reconGo is the compiled program for Debian if you do not want to compile it yourself.
