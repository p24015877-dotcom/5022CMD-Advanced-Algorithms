import threading
import time

FIB_NUMBERS = [35, 38, 40]
ROUNDS = 10


def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def fibonacci_worker(n, results, index):
    start = time.perf_counter_ns()
    value = fibonacci(n)
    end = time.perf_counter_ns()
    results[index] = (n, value, start, end)   # each thread writes only to its own index


def run_with_threads(numbers):
    results = [None] * len(numbers)
    threads = []

    # Create one thread for each Fibonacci number
    for i in range(len(numbers)):
        thread = threading.Thread(target=fibonacci_worker, args=(numbers[i], results, i))
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    first_start = results[0][2]
    last_end = results[0][3]
    values = []
    for n, value, start, end in results:
        if start < first_start:
            first_start = start
        if end > last_end:
            last_end = end
        values.append((n, value))
    return values, last_end - first_start


def run_without_threads(numbers):
    start = time.perf_counter_ns()
    values = []
    for n in numbers:
        values.append((n, fibonacci(n)))
    end = time.perf_counter_ns()
    return values, end - start


def run_experiment(title, run_function, numbers, rounds):
    print(f"\n=== Fibonacci Computation ({title}) ===")
    times = []
    for r in range(1, rounds + 1):
        values, elapsed = run_function(numbers)
        times.append(elapsed)
        fibs = ", ".join(f"Fib({n})={v}" for n, v in values)
        print(f"Round {r:>2}: {fibs} | T = {elapsed:,} ns")
    total = sum(times)
    average = total // len(times)
    print(f"Total T ({title}): {total:,} ns")
    print(f"Average T ({title}): {average:,} ns")
    return average


def main(numbers=FIB_NUMBERS, rounds=ROUNDS):
    avg_threads = run_experiment("With Multithreading", run_with_threads, numbers, rounds)
    avg_single = run_experiment("Without Multithreading", run_without_threads, numbers, rounds)

    difference = (avg_single - avg_threads) / avg_single * 100
    print("\n=== Comparison ===")
    print(f"Average T with multithreading   : {avg_threads:,} ns")
    print(f"Average T without multithreading: {avg_single:,} ns")
    if difference > 0:
        print(f"Observation: Multithreading was {difference:.1f}% faster on average.")
    else:
        print(f"Observation: Multithreading was {-difference:.1f}% slower on average.")


if __name__ == "__main__":
    main()