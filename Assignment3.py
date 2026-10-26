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
    results[index] = (n, value, start, end)


def run_with_threads(numbers):
    results = [None] * len(numbers)
    threads = [threading.Thread(target=fibonacci_worker, args=(n, results, i))
               for i, n in enumerate(numbers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()  # wait for every thread to finish

    first_start = min(r[2] for r in results)
    last_end = max(r[3] for r in results)
    return [(r[0], r[1]) for r in results], last_end - first_start


def run_without_threads(numbers):
    start = time.perf_counter_ns()
    values = [(n, fibonacci(n)) for n in numbers]
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
    average = sum(times) // len(times)
    print(f"Total T ({title}): {sum(times):,} ns")
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