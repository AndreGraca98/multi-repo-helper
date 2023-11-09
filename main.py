from mrh.parser import get_parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    main()
