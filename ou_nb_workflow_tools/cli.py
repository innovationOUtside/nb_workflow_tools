import click
import ou_nb_workflow_tools.imagetable as imagetable

@click.command()
@click.argument('path', default='.', type=click.Path(exists=True))
@click.option('--out_file', '-o', default='gallery.md',  help='Gallery filename')
@click.option('--out_table_type', '-t', default='github',  help='Output table type')
def imagetable_generate(path, out_file, out_table_type):
    """Generate gallery."""
    click.echo(f'Using path: {path}')
    click.echo(f'Writing {out_table_type}-formatted gallery to: {out_file}')
    biglist = imagetable.parse_file_collection(path)
    headers = ['Alt text', 'Image', 'Image Path', 'Path', 'Directory', 'Filename']
    imagetable.write_gallery_file(biglist, headers=headers, typ=out_table_type)
