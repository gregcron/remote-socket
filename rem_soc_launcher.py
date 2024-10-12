import subprocess
import time

def run_script():
    while True:
        print("Starting script...")
        p = subprocess.Popen(['python', 'main.py'])
        start_time = time.time()  # Record the start time

        while True:
            time.sleep(5)  # Check the process every 5 seconds (you can adjust this)

            # Check if 900 seconds have passed or the process has crashed
            if time.time() - start_time > 900:
                print("900 seconds passed. Terminating script...")
                p.terminate()
                p.wait()  # Ensure the process terminates before restarting
                break  # Restart the process by breaking the loop
            elif p.poll() is not None:  # If the process has exited (crashed)
                print(f"Script crashed with exit code {p.returncode}. Restarting...")
                break  # Restart the process

        # Optional delay before restarting the process
        time.sleep(2)

if __name__ == "__main__":
    run_script()
