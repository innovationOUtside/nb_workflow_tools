import click
from pathlib import Path
import nbformat

# Update tags for empinken
# Need to update to use tags: style-activity, style-solution, style-student style-commentate
# Update from tags: style_activity, style_solution, style_student style_commentate
# Update from metadata: 'commentate', 'activity', 'student', 'solution' true/false
@click.command()
@click.argument('path', type=click.Path(resolve_path=False))
def upgrade_empinken_tags(path='.'):
    """Upgrade tags."""

    # Opinionated on this
    version = 4 #nbformat.NO_CONVERT
    typs = ['commentate', 'activity', 'student', 'solution']

    # Iterate path
    nb_dir = Path(path)
    for p in nb_dir.rglob("*"): #nb_dir.iterdir():
        if p.is_file() and p.suffix == '.ipynb':
            print(f"Checking {p}")
            # Read notebook
            with p.open('r') as f:

                # parse notebook
                #nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
                #nb = nbformat.convert(nb, version)
                #opinionated
                nb = nbformat.read(f, as_version=version)
                # for each cell
                for i, _ in enumerate(nb['cells']):
                    metadata = nb['cells'][i]["metadata"]
                    if 'tags' not in metadata:
                        metadata['tags'] = []
                    tags = metadata['tags']
                    for typ in typs:
                        # Upgrade metadata. commentate|activity|student|solution
                        if typ in metadata:
                            metadata.pop(typ, None)
                            tags.append(f'style-{typ}')

                        # Upgrade temporary tags format: style_activity|style_solution|style_student|style_commentate
                        if f'style_{typ}' in metadata.tags:
                            tags.remove(f'style_{typ}')
                            tags.append(f'style-{typ}')

                    # Dedupe
                    metadata['tags'] = list(set(tags))
                    if not metadata['tags']:
                        metadata.pop('tags', None)

                # Validate - exception if we fail
                nbformat.validate(nb)

                # Save notebook
                print(f"Updating {p}: {', '.join(tags)}")
                nbformat.write(nb, p.open('w'), version)
