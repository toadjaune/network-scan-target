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
  - That being said, the risk should be fairly low, and no persistent configuration change is made by this script

- Download the script on your machine
  - TODO : add command examples once we have the github repo URL
- Open a shell on the server, and run :

  - `ulimit -n 200000`
    - This raises the number of files we're allowed to open. The default is typically something like 1024, which is not nearly enough for opening 65535x2 sockets.
    - This is per shell session. If you close your shell and re-open it, you need to run this again
  - `python
