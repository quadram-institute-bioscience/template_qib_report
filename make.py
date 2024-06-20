#!/usr/bin/env python
"""
Automate report generation
"""

import os
import sys
import subprocess
import argparse

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
    args = argparse.ArgumentParser(description='Automate report generation')
    args.add_argument('input', help='Input file')
    args.add_argument('-f', '--force', action='store_true', help='Overwrite output file if it exists')
    args.add_argument('-o', '--output', help='Output file')
    args.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = args.parse_args()

    if not os.path.exists(args.input):
        print('Input file does not exist')
        sys.exit(1)

    inputFileText = open(args.input).read()
    print(f'Input file: {args.input} ({len(inputFileText)} bytes)', file=sys.stderr) if args.verbose else None

    # Determine output format
    outputFormat = None
    if 'EISvogel' not in inputFileText:
        print('Input file is not an expected report file (EISvogel template not detected)')
        exit(1)
    elif 'assets/titlepageFig.pdf' in inputFileText:
        outputFormat = 'pdf'
    elif '- assets/pandoc3.css' in inputFileText:
        outputFormat = 'html'
    else:
        print('Input file is not an expected report file (expected format not detected)')
        exit(1)
    print(f'Output format: {outputFormat}', file=sys.stderr) if args.verbose else None
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
            print('Output file exists, overwriting')
        else:
            print('Output file exists, use -f to overwrite')
            exit(1)

    print(f'Output file: {outputFile}', file=sys.stderr) if args.verbose else None

    scriptDir = os.path.dirname(os.path.realpath(__file__))
    check_deps()
 
        
    cmd = None
    if outputFormat == 'pdf':
        cmd = ['pandoc', os.path.abspath(args.input), '-o', outputFile, '--from', 'markdown', '--template', 'assets/eisvogel', '--listings']
    else:
        cmd = ['pandoc', os.path.abspath(args.input), '-o', outputFile, '--toc']

    try:
        subprocess.check_call(cmd)
        if os.path.exists(outputFile):
            print(f'Output file created: {outputFile}')
    except subprocess.CalledProcessError as e:
        print('Error while running pandoc')
        print("\t", e)
        sys.exit(1)
if __name__ == '__main__':
    main()