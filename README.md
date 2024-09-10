# What is this thing ?

You've got a firewall that you either can't inspect the configuration of, or you want to debug said configuration.

Either way, you want to do some black box testing on said firewall.

To do this, you need two machines, one on each side of this firewall.

There's plethora of tooling available on the client machine (the one initially connecting to the other) that you're going to use.
Typically, that would be `nmap` or some of its friends (`telnet`, `netcat`, etc).

On the server side, though, you need something that will always answer to such a probe, so that you can probe it from the client, and determine whether the firewall is blocking traffic between the two or you, or not.

That's what this repo offers.

# How do I use it ?

## Server setup

- No specific server-side setup is required, only python3 with the stdlib.
- If you can, create a dedicated VM for this, rather than using a machine with a real use.

  - We're going to open sockets on EVERY port, TCP and UDP. Meaning that once we're running, nothing else can claim any port, and some programs might behave poorly in such a situation. You've been warned.
  - Also, zero effort was made at performance optimization. You should probably take a beefy VM if you want it to hold.
  - That being said, no persistent configuration change is made by this script

- Download the script on your machine, with for example :
  - git clone https://github.com/toadjaune/network-scan-target.git
  - curl -O https://raw.githubusercontent.com/toadjaune/network-scan-target/main/listen.py
- Open a shell on the server, and run :

  - `ulimit -n 200000`
    - This raises the number of files we're allowed to open. The default is typically something like 1024, which is not nearly enough for opening 65535x2 sockets.
    - This is per shell session. If you close your shell and re-open it, you need to run this again
  - `./listen.py`
    - You're gonna need to be root to bind to ports <1024, use `sudo` if necessary, or use the `--port-min` argument.
    - This command never exits, that's normal, it's a server. Exit with Ctrl-C when you're done testing.

- To avoid jumping to wrong conclusions regarding the blackbox firewall, I'd advise to first attempt scanning from the server itself, then from a host where you know that it's supposed to work.
  - This can help put in light configuration errors somewhere else in the setup (say, the server is an AWS VM, and you messed up your security group setup...)

## Client setup

- Install `nmap`, `telnet`, `netcat` using your operating system's package manager :
  - debian/ubuntu-based : `sudo apt install nmap telnet`
  - redhat/fedora-based : `sudo dnf install nmap telnet`
  - other linux distribution : You probably know how
  - MacOS : Set up [homebrew](https://brew.sh/), then `brew install nmap telnet`
  - Windows : That's probably doable with git-bash or wsl2. Feel free to submit a PR if you use such an environment ; I don't.

## Running a test from the client

Think of this section of basic examples with the tools installed above.
It's by no means an exhaustive listing of what can be done with those tools.
Use a search engine and read manpages :)

### Test a specific port

- TCP : `telnet <target_host> <target_port>`
- TCP : `nc    <target_host> <target_port>`
- UDP : `nc -u <target_host> <target_port>` (then press enter)
- TCP : `nmap     -p <target_port> <target_host>`
- UDP : `nmap -sU -p <target_port> <target_host>`

### Port range

- TCP : `nmap     -p 1-65535 <target_host> -dd | grep -E "^[[:digit:]]+/" | grep -v " open "`
- UDP : `nmap -sU -p 1-65535 <target_host> -dd | grep -E "^[[:digit:]]+/" | grep -v " open "`

# Cool, but I wish it did $SOME_FEATURE, is this possible ?

This is a quick'n dirty script that I wrote the one time I needed it.
Feel free to use it, but I'm not planning to have it become a proper clean software.

PRs are welcome though :)

# Related projects and inspirations

http://portquiz.net/ is pretty cool, and probably sufficient if :

- The firewall that you're testing is between you and "the Internet"
- You only need TCP testing
- You only need to test a few ports manually, not the entire range
