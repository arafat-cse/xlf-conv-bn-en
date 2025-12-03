import xml.etree.ElementTree as ET
import os
import argparse
from pathlib import Path
from deep_translator import GoogleTranslator
from time import sleep
from tqdm import tqdm

from xlf_utils import XLFParseError, parse_xlf_document

ET.register_namespace('', 'urn:oasis:names:tc:xliff:document:1.2')

def translate_xlf_to_english(input_file, output_file):
    translator = GoogleTranslator(source='bn', target='en')
    parsed = parse_xlf_document(Path(input_file))
    tree = parsed.tree
    root = tree.getroot()
    if parsed.recovered:
        print("Warning: Input XML contained structural issues. Proceeding with recovered content.")
    ns = {'xliff': 'urn:oasis:names:tc:xliff:document:1.2'}
    trans_units = root.findall('.//xliff:trans-unit', ns)
    total_units = len(trans_units)
    print(f"Found {total_units} <trans-unit> elements in {input_file}")
    failed_translations = []
    GREEN = "\033[38;2;137;243;54m"
    RED = "\033[38;2;255;0;0m"
    RESET = "\033[0m"
    progress_bar = tqdm(
        total=total_units,
        desc=f"{GREEN}Translating{RESET}",
        unit="unit",
        bar_format=f"{GREEN}{{bar}}{RESET}| {GREEN}{{n_fmt}}/{{total_fmt}} [{GREEN}{{elapsed}}<{GREEN}{{remaining}}]{RESET}"
    )

    for trans_unit in trans_units:
        source = trans_unit.find('xliff:source', ns)
        if source is None or not source.text:
            print(f"Skipping trans-unit {trans_unit.get('id')} with no valid source text")
            progress_bar.update(1)
            continue

        target = trans_unit.find('xliff:target', ns)
        if target is None:
            target = ET.Element('{urn:oasis:names:tc:xliff:document:1.2}target')
            source_index = list(trans_unit).index(source)
            trans_unit.insert(source_index + 1, target)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    translated = translator.translate(source.text)
                    target.text = translated
                    break
                except Exception as e:
                    print(f"Error translating '{source.text}' ID: {trans_unit.get('id')}, On attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        sleep(2)
                        continue
                    failed_translations.append({
                        'id': trans_unit.get('id'),
                        'source': source.text,
                        'error': str(e)
                    })

        progress_bar.update(1)

    progress_bar.close()

    if failed_translations:
        print("\nFailed Translations:")
        for fail in failed_translations:
            print(f"ID: {fail['id']}, Source: '{fail['source']}', Error: {fail['error']}")

    print("Completed")
    failed_count = len(failed_translations)
    color = GREEN if failed_count == 0 else RED
    print(f"{color}Failed: {failed_count}{RESET}")
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"Translated XLF file saved as {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Add <target> tags with English translations of <source> (Bangla) in XLF file if missing")
    parser.add_argument('--input', default='/var/www/html/GTrn/xlf-conv-bn-en/input.xlf', help='Input XLF file path')
    parser.add_argument('--output', default='/var/www/html/GTrn/xlf-conv-bn-en/output_English.xlf', help='Output XLF file path')
    args = parser.parse_args()

    if os.path.exists(args.input):
        try:
            translate_xlf_to_english(args.input, args.output)
        except XLFParseError as exc:
            print(f"Failed to parse input XLF: {exc}")
    else:
        print(f"Input file {args.input} not found")

if __name__ == "__main__":
    main()
