import click
from pathlib import Path
import nbformat

# Update tags for empinken
# Need to update to use tags: style-activity, style-solution, style-learner style-tutor
# Update from tags: style_activity, style_solution, style_student style_commentate
# Update from metadata: 'commentate', 'activity', 'student', 'solution' true/false
@click.command()
@click.argument('path', type=click.Path(resolve_path=False))
def upgrade_empinken_tags(path='.'):
    """Upgrade tags."""
    def _upgrade_file(p):
        if p.is_file() and p.suffix == '.ipynb':
            print(f"Checking {p}")
            # Read notebook
            with p.open('r') as f:

                # parse notebook
                # nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
                # nb = nbformat.convert(nb, version)
                # opinionated
                nb = nbformat.read(f, as_version=version)
                # for each cell
                for i, _ in enumerate(nb['cells']):
                    metadata = nb['cells'][i]["metadata"]
                    if 'tags' not in metadata:
                        metadata['tags'] = []
                    tags = metadata['tags']
                    for typ in typs:
                        # Upgrade metadata . tutor|activity|learner|solution
                        if typ in metadata:
                            metadata.pop(typ, None)
                            tags.append(f'style-{new_typs[typ]}')

                        # Upgrade original tags format: style_activity|style_solution|style_student|style_commentate
                        if f'style_{typ}' in metadata.tags:
                            tags.remove(f'style_{typ}')
                            tags.append(f'style-{new_typs[typ]}')

                    # Dedupe
                    metadata['tags'] = list(set(tags))
                    if not metadata['tags']:
                        metadata.pop('tags', None)

                # Validate - exception if we fail
                nbformat.validate(nb)

                # Save notebook
                print(f"Updating {p}: {', '.join(tags)}")
                nbformat.write(nb, p.open('w'), version)

    # Opinionated on this
    version = 4 #nbformat.NO_CONVERT
    typs = ['commentate', 'activity', 'student', 'solution']
    new_typs = {"commentate":"tutor", "activity":"activity",
    "student":"learner", "solution":"solution"}

    # Iterate path
    nb_path = Path(path)
    if nb_path.is_file():
        _upgrade_file(nb_path)
    else:
        for p in nb_path.rglob("*"):  # nb_dir.iterdir():
            _upgrade_file(p)
