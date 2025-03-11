import os
import argparse

"""
# Ottieni la directory dello script in esecuzione
script_dir = os.path.dirname(os.path.realpath(__file__))

# Definizione degli argomenti della riga di comando
parser = argparse.ArgumentParser(description='Save input directory path to a text file.')
parser.add_argument('-i', '--input', metavar='', required=True, help='Path to the input directory')
args = parser.parse_args()

# Percorso del file di output
output_file = os.path.join(script_dir, "input_path.txt")

# Se il file esiste già, lo elimina
if os.path.exists(output_file):
    os.remove(output_file)

# Scrive il percorso nel file
with open(output_file, "w") as file:
    file.write(args.input)

print(f"Il percorso è stato salvato in {output_file}")
"""


def save_paths(input_path, work_path, output_file):
    """
    Salva i percorsi dell'input e della work directory in un file di testo.
    """
    with open(output_file, "w") as file:
        file.write(input_path + "\n")
        file.write(work_path + "\n")

if __name__ == "__main__":
    # Ottieni la directory dello script in esecuzione
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Definizione degli argomenti della riga di comando
    parser = argparse.ArgumentParser(description='Save input and work directory paths to a text file.')
    parser.add_argument('-i', '--input', metavar='', required=True, help='Path to the input directory')
    parser.add_argument('-w', '--work', metavar='', required=True, help='Path to the work directory')
    args = parser.parse_args()
    
    # Percorso del file di output
    output_file = os.path.join(script_dir, "input_path.txt")
    
    # Se il file esiste già, lo elimina
    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Salva i percorsi nel file
    save_paths(args.input, args.work, output_file)
    
    print(f"I percorsi sono stati salvati in {output_file}")
