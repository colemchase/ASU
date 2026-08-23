import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor

# Task 1: Data Processing (Sorting a large dataset)
def data_processing():
    print("Starting Data Processing...")
    data = [random.randint(1, 1000000) for _ in range(100000)]
    sorted_data = sorted(data)
    print("Data Processing Complete")
    return len(sorted_data)

# Task 2: Simulated Database Query
def database_query():
    print("Simulating Database Query...")
    time.sleep(0.5)  # Simulate database query delay
    print("Database Query Complete")
    return "Query Complete"

# Task 3: API Request to External Service
def api_request():
    print("Sending API Request...")
    try:
        response = requests.get("https://jsonplaceholder.typicode.com/posts")
        print(f"API Response: {response.status_code}, Time: {response.elapsed.total_seconds()}s")
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

# Task 4: File I/O Operation
def file_io():
    print("Starting File I/O Task...")
    filename = "test_file.txt"
    with open(filename, "w") as f:
        f.write("Load testing simulation. " * 10000)
    with open(filename, "r") as f:
        content = f.read()
    print("File I/O Task Complete")
    return len(content)

# Task 5: CPU-Intensive Computation
def computation_task():
    print("Starting Computation Task...")
    result = sum(x ** 2 for x in range(10000))
    print("Computation Task Complete")
    return result

# Task 6: Logging to File
def logging_task():
    print("Starting Logging Task...")
    with open("log.txt", "a") as log_file:
        log_file.write(f"Task executed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    print("Logging Task Complete")
    return "Log Written"

# Function to Execute All Tasks
def execute_tasks():
    return {
        "Data Processing": data_processing(),
        "Database Query": database_query(),
        "API Request": api_request(),
        "File I/O": file_io(),
        "Computation Task": computation_task(),
        "Logging Task": logging_task(),
    }

# Multi-threaded Load Simulation
def load_testing(concurrent_users):
    print(f"Starting Load Test with {concurrent_users} users...")
    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(execute_tasks) for _ in range(concurrent_users)]
        results = [future.result() for future in futures]
    return results

if __name__ == "__main__":
    # Define number of users to simulate
    concurrent_users = 10

    # Start Load Test
    start_time = time.time()
    results = load_testing(concurrent_users)
    end_time = time.time()

    print("Load Test Complete!")
    print(f"Total Execution Time: {end_time - start_time:.2f} seconds")
    print("Sample Results for Two Users:")
    for result in results[:2]:  # Print results of the first two users
        print(result)
