import click

@click.command(options_metavar='<Options>')
@click.argument('arg',metavar='Argument')

def main():
    print("Hola!")


if __name__ == '__main__':
    main()
