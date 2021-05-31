from flask import Flask
import os
import subprocess

user = "TheSlowGrowth"
repo = "daisyHat_Examples"
token = os.environ["GITHUB_RUNNER_TOKEN"]
dockerImageName = "actions-image"
runnerName = "daisyhat-runner"

app = Flask(__name__)

def spinUpRunner():
    command = ["docker", "run", "--rm", "-d", dockerImageName, user, repo, token, runnerName]
    result = subprocess.run(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            timeout=20,
                            check=False)
    print(result.stdout.decode("utf-8"))

def stopAllRunners():
    # get IDs of all running containers
    command = ["docker", "ps", "-aq", "--filter", "ancestor="+dockerImageName]
    containersToStop = subprocess.run(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            timeout=20,
                            check=False).stdout.decode("utf-8").split()
    # stop all running containers - send SIGINT to let them shutdown (doesn't work apparently)
    command = ["docker", "kill", "--signal=SIGINT"] + containersToStop
    result = subprocess.run(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            timeout=40,
                            check=False)
    print(result.stdout.decode("utf-8"))
    # stop all running containers - forcefully quit whatever is still running 
    command = ["docker", "stop", "--time=30"] + containersToStop    
    result = subprocess.run(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            timeout=40,
                            check=False)
    print(result.stdout.decode("utf-8"))
    # remove all running containers
    command = ["docker", "rm"] + containersToStop
    result = subprocess.run(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            timeout=20,
                            check=False)
    print(result.stdout.decode("utf-8"))
    return containersToStop

@app.route('/start')
def start():
    stopAllRunners()
    spinUpRunner()
    return 'Runner started.'

@app.route('/stop')
def stop():
    runnersStopped = stopAllRunners()
    return 'Runners stopped:' + str(runnersStopped)
