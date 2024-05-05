from model.simulate import simulate_command
from model.simulation_options import SimulationOptions
from nlv_args import NLVArgs, merge_obj, parse_args


def main():
    args: NLVArgs = parse_args()

    for i, config in enumerate(args.configs):
        args.current_index = i
        match args.action:
            case "simulate":
                args.configs[i] = merge_obj(SimulationOptions(), config)
                simulation = simulate_command(args)

            case "generate":
                
                pass
                
                # run_random()


if __name__ == "__main__":
    main()
