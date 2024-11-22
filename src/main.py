from router import MazeRouter


def main():
    input_file = 'test_cases/case3_obstacles.txt'
    output_file = 'output.txt'  # Replace with the path for your output file

    # Initialize MazeRouter with the input file
    router = MazeRouter(input_file)
    
    # Try to route all nets
    if router.route_all_nets(max_attempts=15):
        print("Routing successful!")
    else:
        print("Routing failed after maximum attempts.")
    
    # Write the output to the specified file
    router.write_output(output_file)
    print(f"Routing results written to {output_file}")
    
    
if __name__ == "__main__":
    main()