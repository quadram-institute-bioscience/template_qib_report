#!/usr/bin/env python
"""
Automate report generation
"""

import os
import sys
import subprocess
import argparse
import re
import tempfile
import datetime
import csv


def striptags(s):
    """
    Strip {color:red} and other tags from JIRA text
    """
    text = re.sub(r'\{[^}]+\}', '', s)
    return re.sub(r'\n', '\n\n', text)

def getTicket(id):
    path = None
    paths = ['/Volumes/Research-Groups/CoreBioInfo/tickets/issues.csv',
             '/qib/research-groups/CoreBioInfo/tickets/issues.csv']

    if os.path.exists(paths[0]):
        path = paths[0]
    elif os.path.exists(paths[1]):
        path = paths[1]

    if not path:
        print('Tickets CSV File not found')
        sys.exit(1)
    
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            if row['issue_key'] == id:
                row['desc'] = striptags(row['description'])
                return row

def H(s, color='green'):
    """
    highlight a string text (terminal)
    """
    if color == 'green':
        return f'\033[92m{s}\033[0m'
    elif color == 'red':
        return f'\033[91m{s}\033[0m'
    elif color == 'blue':
        return f'\033[94m{s}\033[0m'
    elif color == 'yellow':
        return f'\033[93m{s}\033[0m'
    elif color == 'bold':
        return f'\033[1m{s}\033[0m'

def get_snippets(directory):
    """
    get all .md files in a directory and create a dictionary of names and conents
    """
    snippets = {}
    if not os.path.exists(directory):
        raise FileNotFoundError(f'Directory {directory} does not exist')
    for f in os.listdir(directory):
        if f.endswith('.md'):
            with open(os.path.join(directory, f)) as snippetFile:
                snippets[f.replace('.md', '')] = snippetFile.read()

            # if f == 'glossary.md' sort all lines exept the first two
            if f == 'glossary':
                lines = snippets[f].split('\n')
                lines = lines[:2] + sorted(lines[4:])
                snippets[f] = '\n'.join(lines)
    return snippets

def check_deps(outputFormat='html'):
    """
    Check some essential dependencies are available
    """
    # Check pandoc suppressing all output
    if subprocess.call(['pandoc', '-v'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        print('Pandoc is not installed')
        sys.exit(1)

    if outputFormat == 'pdf':
        # Check LaTeX
        if subprocess.call(['pdflatex', '-v'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            print('pdflatex is not installed')
            sys.exit(1)
def main():
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    args = argparse.ArgumentParser(description='Automate report generation')
    args.add_argument('input', help='Input file')
    args.add_argument('-f', '--force', action='store_true', help='Overwrite output file if it exists')
    args.add_argument('-d', '--date-update', help='Update date', action='store_true')
    args.add_argument('-o', '--output', help='Output file')
    args.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = args.parse_args()

    if not os.path.exists(args.input):
        print('Input file does not exist')
        sys.exit(1)

    ticketID = None
    ticketRe = re.compile(r'(BSUP-\d+)')
    match = ticketRe.search(args.input)
    if match:
        ticketID = match.group(1)
        print(f'Ticket ID:\t{H(ticketID)}', file=sys.stderr) if args.verbose else None
        ticket = getTicket(ticketID)
   
    else:
        print(f'No ticket ID found in {H(args.input)}', file=sys.stderr) if args.verbose else None
    inputFileText = open(args.input).read()
    print(scriptDir)
    print(f'Input file:\t{H(args.input)} ({len(inputFileText)} bytes)', file=sys.stderr) if args.verbose else None
    
    


    # Determine output format
    outputFormat = None
    if 'pandoc -V fontsize=12pt -V geometry:margin=1in' not in inputFileText:
        print('Input file is not an expected report file (EISvogel template not detected)')
        exit(1)
    elif 'assets/titlepageFig.pdf' in inputFileText:
        outputFormat = 'pdf'
    elif '- assets/pandoc3.css' in inputFileText:
        outputFormat = 'html'
    else:
        print('Input file is not an expected report file (expected format not detected)')
        exit(1)
    print(f'Output format:\t{H(outputFormat)}', file=sys.stderr) if args.verbose else None
    
    
    # Update input file

    if args.date_update:
        regex = r'date: "(\d+)[./-](\d+)[./-](\d+)"'
        today = datetime.date.today()
        newDate = today.strftime('%Y-%m-%d')
        print(f'Updating date:\t{H(newDate, color="yellow")}')
        """
        highlight a string text (terminal)
        """
        inputFileText = re.sub(regex, f'date: "{newDate}"', inputFileText)
    ## Insert snippets
    if '[[' in inputFileText: 
        snippets = get_snippets(os.path.join(scriptDir, 'assets', 'snippets'))
        print(f'Found {H(len(snippets))} snippets') if args.verbose else None
        # Regex to find like [[filename.md]]
        regex = r'\[\[(.*?)\]\]'
        
        for match in re.finditer(regex, inputFileText):
            snippetName = match.group(1)
            if snippetName not in snippets:
                print(f'ERROR: Snippet {H(snippetName, color="red")} not found: {snippets.keys()}')
                exit(1)
            print(f'Inserting snippet {H(snippetName)}') if args.verbose else None
            inputFileText = inputFileText.replace(f'[[{snippetName}]]', snippets[snippetName])
    # Insert ticket information

    key_re = r'\{\{([^\}]+)\}\}'
    for match in re.finditer(key_re, inputFileText):
        key = match.group(1)
        if key in ticket:
            print(f'Inserting ticket key {H(key)}') if args.verbose else None
            inputFileText = inputFileText.replace(f'{{{{{key}}}}}', ticket[key])
        else:
            print(f'ERROR: Ticket key {H(key, color="red")} not found: {ticket.keys()}')
            exit(1)
    # Save updated input file
    tempInputFile = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md', dir=os.path.dirname(args.input))
    tempInputFile.write(inputFileText)
    tempInputFile.close()
    print(f'Temporary file:\t{H(tempInputFile.name)}', file=sys.stderr) if args.verbose else None
    

    # Output file
    if not args.output:
        
        outputFile = os.path.basename(args.input).replace('.md', '.pdf' if outputFormat == 'pdf' else '.html')
        outputFile = os.path.join(os.path.dirname(args.input), outputFile)
    elif args.output.endswith('.pdf') and outputFormat != 'pdf':
        print('Output file should have a .html extension?')
        exit(1)
    elif args.output.endswith('.html') and outputFormat != 'html':
        print('Output file should have a .pdf extension?')
        exit(1)
    else:
        outputFile =  os.path.abspath(args.output)

    if os.path.exists(outputFile):
        if args.force:
            print(f'{H('WARNING:', color='yellow')}\tOutput file exists, overwriting')
        else:
            print('Output file exists, use -f to overwrite')
            exit(1)

    print(f'Output file:\t{H(outputFile)}', file=sys.stderr) if args.verbose else None
    

    
    check_deps()
 
        
    cmd = None
    if outputFormat == 'pdf':
        cmd = ['pandoc', os.path.abspath(tempInputFile.name), '-o', outputFile, '--from', 'markdown', '--template', 'assets/eisvogel', '--listings']
    else:
        cmd = ['pandoc', os.path.abspath(tempInputFile.name), '-o', outputFile, '--toc']

    try:
        subprocess.check_call(cmd)
        if os.path.exists(outputFile):
            print(f'Output created: {H(outputFile)}')
            """
            highlight a string text (terminal)
            """
            os.unlink(tempInputFile.name)
    except subprocess.CalledProcessError as e:
        print('Error while running pandoc')
        print("\t", e)
        sys.exit(1)
    
    
if __name__ == '__main__':
    main()