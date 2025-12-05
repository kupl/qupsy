from synthesizer.search import search_base
import argparse, time

# python qpsynth.py benchmarks/ghz.json baseline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark", type=str, help="Benchmark to run")
    parser.add_argument("search", choices=["baseline"], help="Search method")
    args = parser.parse_args()

    start = time.time()
    if args.search == "baseline":
        result = search_base(args.benchmark)
    print(str(result))
    end = time.time()
    print(f"Time: {end-start}")


if __name__ == "__main__":
    main()
