"""
Script zum Extrahieren von AIR IDs aus HTML
Sucht nach Zeilen mit "Click to copy AIR ID" und extrahiert IDs im Format string:int@int
"""

import re
import sys
import argparse
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


def is_valid_url(url: str) -> bool:
    """Prüft ob es sich um eine gültige URL handelt."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def fetch_html(url: str) -> str:
    """Lädt HTML von einer URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Fehler beim Laden der URL: {e}")


def extract_air_ids(html: str) -> list:
    """
    Extrahiert AIR IDs aus HTML.
    Sucht nach Zeilen mit "Click to copy AIR ID" und extrahiert 
    den Teil zwischen >< im Format string:int@int
    """
    air_ids = []
    
    # Pattern für das Format string:int@int
    # z.B. "abc:123@456" oder "test:42@789"
    pattern = r'([a-zA-Z0-9_-]+):(\d+)@(\d+)'
    
    # HTML in Zeilen aufteilen
    lines = html.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Prüfe ob die Zeile "Click to copy AIR ID" enthält
        if "Click to copy AIR ID" in line:
            # Suche nach dem Pattern zwischen ><
            # Finde alle Vorkommen von >...< in dieser Zeile
            matches = re.finditer(r'>([^<]+)<', line)
            
            for match in matches:
                content = match.group(1)
                # Prüfe ob der Inhalt dem Pattern entspricht
                id_match = re.search(pattern, content)
                if id_match:
                    full_match = id_match.group(0)
                    air_ids.append({
                        'id': full_match,
                        'line': line_num,
                        'context': content.strip()
                    })
    
    return air_ids


def extract_air_ids_alternative(html: str) -> list:
    """
    Alternative Methode: Verwendet BeautifulSoup für bessere HTML-Parsing
    """
    air_ids = []
    pattern = r'([a-zA-Z0-9_-]+):(\d+)@(\d+)'
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Finde alle Elemente die "Click to copy AIR ID" enthalten
        elements = soup.find_all(string=re.compile("Click to copy AIR ID"))
        
        for element in elements:
            # Gehe zum Parent-Element
            parent = element.parent
            
            # Suche nach Text der dem Pattern entspricht im Parent oder Geschwistern
            if parent:
                # Suche im gesamten Parent-Baum
                text_content = parent.get_text()
                matches = re.finditer(pattern, text_content)
                
                for match in matches:
                    full_match = match.group(0)
                    # Prüfe ob es wirklich zwischen >< ist
                    parent_html = str(parent)
                    if full_match in parent_html:
                        air_ids.append({
                            'id': full_match,
                            'context': text_content.strip()[:100]  # Erste 100 Zeichen
                        })
    except Exception as e:
        print(f"⚠️  BeautifulSoup Parsing Fehler: {e}", file=sys.stderr)
    
    return air_ids


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(
        description="Extrahiert AIR IDs aus HTML einer Website",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Von URL:
  python extract_air_ids.py --url https://example.com/page
  
  # Von lokaler HTML-Datei:
  python extract_air_ids.py --file page.html
  
  # Mit alternativer Parsing-Methode:
  python extract_air_ids.py --url https://example.com/page --use-soup
        """
    )
    
    parser.add_argument(
        "--url",
        type=str,
        help="URL der Website"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Pfad zur lokalen HTML-Datei"
    )
    
    parser.add_argument(
        "--use-soup",
        action="store_true",
        help="Verwende BeautifulSoup für Parsing (experimentell)"
    )
    
    args = parser.parse_args()
    
    # HTML laden
    html = None
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                html = f.read()
            print(f"✅ HTML-Datei geladen: {args.file}")
        except FileNotFoundError:
            print(f"❌ Datei nicht gefunden: {args.file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Fehler beim Lesen der Datei: {e}")
            sys.exit(1)
    
    elif args.url:
        if not is_valid_url(args.url):
            print(f"❌ Ungültige URL: {args.url}")
            sys.exit(1)
        
        try:
            print(f"🔄 Lade HTML von: {args.url}")
            html = fetch_html(args.url)
            print("✅ HTML erfolgreich geladen")
        except Exception as e:
            print(f"❌ Fehler: {e}")
            sys.exit(1)
    
    else:
        print("❌ Bitte geben Sie entweder --url oder --file an")
        parser.print_help()
        sys.exit(1)
    
    # AIR IDs extrahieren
    print("\n🔄 Suche nach AIR IDs...")
    
    if args.use_soup:
        air_ids = extract_air_ids_alternative(html)
    else:
        air_ids = extract_air_ids(html)
    
    # Ergebnisse anzeigen
    print(f"\n{'='*80}")
    print(f"GEFUNDENE AIR IDs: {len(air_ids)}")
    print(f"{'='*80}\n")
    
    if air_ids:
        for i, item in enumerate(air_ids, 1):
            print(f"{i}. {item['id']}")
            if 'line' in item:
                print(f"   Zeile: {item['line']}")
            if 'context' in item:
                context = item['context']
                if len(context) > 80:
                    context = context[:77] + "..."
                print(f"   Kontext: {context}")
            print()
    else:
        print("⚠️  Keine AIR IDs gefunden")
        print("\n💡 Tipp:")
        print("   - Stelle sicher, dass die Seite 'Click to copy AIR ID' enthält")
        print("   - Prüfe ob das Format 'string:int@int' korrekt ist")
        print("   - Versuche --use-soup für alternative Parsing-Methode")
    
    # Als Liste ausgeben (für weitere Verarbeitung)
    if air_ids:
        print(f"\n{'='*80}")
        print("AIR IDs (nur IDs):")
        print(f"{'='*80}")
        for item in air_ids:
            print(item['id'])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Abgebrochen vom Benutzer")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

