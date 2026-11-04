"""Modelli di disdetta scaricabili (.docx e .pdf), generati al build.
Il testo della lettera è lo stesso del generatore JS (genLettera in build.py), con i campi da compilare tra parentesi quadre.
I file sono deterministici (date fisse) per non cambiare a ogni build.
"""
import io, re, zipfile

DATA_FISSA = (2026, 1, 1, 0, 0, 0)


def testo_lettera(d, leggi, campo, servizio):
    """Porta in Python di genLettera() con i segnaposto al posto dei dati dell'utente."""
    cat = d["cat"]; L = leggi.get(cat, leggi["altri-servizi"])
    nome = "[Nome e cognome]"; ind = "[Indirizzo di residenza]"; cf = "[Codice fiscale]"; mail = "[La tua e-mail]"
    cod = "[Codice cliente / numero di contratto]"; linea = "[se presente]"; luogo = "[Luogo]"; oggi = "[Data]"
    rifC = "n. " + cod + " (" + campo + " " + linea + ")"
    t = nome + "\n" + ind + "\nC.F. " + cf + "\n" + mail + "\n\n"
    t += "Spett.le " + d["azienda"] + ("\n" + d["postale"] if d["postale"] else "") + ("\nPEC: " + d["pec"] if d["pec"] else "") + "\n\n"
    t += luogo + ", " + oggi + "\n\n" + ("Trasmessa a mezzo posta elettronica certificata (PEC)" if d["pec"] else "Raccomandata con avviso di ricevimento") + "\n\n"
    t += "OGGETTO: " + ("disdetta della polizza " if cat == "assicurazioni" else "richiesta di cessazione della fornitura - contratto " if cat == "energia" else "recesso dal contratto ") + rifC + "\n\n"
    t += "Il/La sottoscritto/a " + nome + ", codice fiscale " + cf + ", residente in " + ind + ", in qualità di intestatario/a del contratto " + rifC + " relativo " + servizio + ",\n\n"
    t += "COMUNICA\n\n"
    if cat == "assicurazioni":
        t += "la propria disdetta della suddetta polizza " + L["rif"] + "."
    else:
        t += "la propria volontà di recedere dal suddetto contratto, " + L["rif"] + ", con effetto dalla scadenza del termine di preavviso previsto" + (", che non può essere superiore a trenta giorni" if cat in ("telefonia", "tv-streaming") else "") + "."
    t += "\n\nCHIEDE\n\n"
    ext = L.get("extra", "") if cat in ("telefonia", "tv-streaming", "energia") else ""
    t += "- la cessazione " + ("della copertura alla scadenza" if cat == "assicurazioni" else "della fornitura" if cat == "energia" else "del servizio") + (" " + ext if ext else ";") + "\n"
    if L.get("app"):
        t += "- " + L["app"] + "\n"
    t += "- l'interruzione di ogni addebito successivo alla data di efficacia del recesso, comprese eventuali domiciliazioni bancarie o addebiti su carta di credito collegati al contratto;\n"
    if cat in ("assicurazioni", "palestre"):
        ex = L["extra"]; t += "- " + ex[0].lower() + re.sub(r"\.$", ";", ex[1:]) + "\n"
    t += "- conferma scritta della ricezione della presente e della data di cessazione del contratto, all'indirizzo " + mail + ".\n\n"
    t += "I dati personali contenuti nella presente sono comunicati al solo fine di dare esecuzione al recesso, ai sensi del Regolamento (UE) 2016/679.\n\n"
    t += "Si allega copia di un documento di identità in corso di validità.\n\nDistinti saluti.\n\n" + nome + "\n\n____________________\n(firma)"
    return t


# ---------- DOCX (python-docx, poi zip réécrit avec dates fixes) ----------
def docx_bytes(titolo, istruzioni, lettera):
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_COLOR_INDEX
    import datetime as dt
    doc = Document()
    cp = doc.core_properties
    cp.author = "disdettaabbonamento.it"; cp.title = titolo; cp.last_modified_by = "disdettaabbonamento.it"
    cp.created = cp.modified = dt.datetime(*DATA_FISSA); cp.revision = 1
    h = doc.add_paragraph(); r = h.add_run(titolo); r.bold = True; r.font.size = Pt(15)
    for riga in istruzioni:
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(2)
        r = p.add_run(riga); r.italic = True; r.font.size = Pt(9.5); r.font.color.rgb = RGBColor(0x58, 0x64, 0x7a)
    doc.add_paragraph("_" * 60)
    for blocco in lettera.split("\n\n"):
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(8)
        righe = blocco.split("\n")
        for i, riga in enumerate(righe):
            bold = riga in ("COMUNICA", "CHIEDE") or riga.startswith("OGGETTO:")
            for parte in re.split(r"(\[[^\]]+\])", riga):
                if not parte: continue
                r = p.add_run(parte); r.bold = bold
                if parte.startswith("["): r.font.highlight_color = WD_COLOR_INDEX.YELLOW
            if i < len(righe) - 1: p.add_run().add_break()
    buf = io.BytesIO(); doc.save(buf)
    # Alleggerimento: via le parti inutili del template (stili con effetti, miniatura, customXml), stili minimi
    src = zipfile.ZipFile(io.BytesIO(buf.getvalue())); out = io.BytesIO()
    via = ("word/stylesWithEffects.xml", "docProps/thumbnail.jpeg", "customXml/")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in src.infolist():
            nome = info.filename
            if nome.startswith(via): continue
            dati = src.read(nome)
            if nome == "word/styles.xml": dati = STILI_MIN.encode()
            elif nome.endswith(".rels") or nome == "[Content_Types].xml":
                t = dati.decode()
                t = re.sub(r'<Relationship [^>]*Target="(stylesWithEffects\.xml|docProps/thumbnail\.jpeg|\.\./customXml/item1\.xml)"/>', "", t)
                t = re.sub(r'<Override PartName="/(word/stylesWithEffects\.xml|customXml/[^"]*)"[^>]*/>', "", t)
                dati = t.encode()
            zi = zipfile.ZipInfo(nome, DATA_FISSA); zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, dati)
    return out.getvalue()


STILI_MIN = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
             '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" w:cs="Calibri"/>'
             '<w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="it-IT"/></w:rPr></w:rPrDefault>'
             '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
             '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
             '<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont"><w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/></w:style>'
             '</w:styles>')


# ---------- PDF (scritto a mano: Helvetica, WinAnsiEncoding) ----------
_W = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 + \
     [278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
      667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556, 556, 500, 556, 556,
      278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]
_BASE = str.maketrans("àáâäèéêëìíîïòóôöùúûüÀÁÈÉÌÍÒÓÙÚçÇñ", "aaaaeeeeiiiioooouuuuAAEEIIOOUUcCn")


def _larg(s, size, bold=False):
    w = 0
    for ch in s.translate(_BASE):
        o = ord(ch); w += _W[o - 32] if 32 <= o < 127 else 556
    return w * size / 1000 * (1.07 if bold else 1)


def _wrap(s, size, maxw, bold=False):
    if not s: return [""]
    out, cur = [], ""
    for parola in s.split(" "):
        prova = (cur + " " + parola) if cur else parola
        if _larg(prova, size, bold) <= maxw or not cur: cur = prova
        else: out.append(cur); cur = parola
    out.append(cur); return out


def _esc(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    b = s.encode("cp1252", "replace")
    return b.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def pdf_bytes(titolo, istruzioni, lettera):
    PW, PH, M = 595, 842, 50; maxw = PW - 2 * M
    righe = []  # (testo, font, size, grigio, leading)
    for r in _wrap(titolo, 15, maxw, True): righe.append((r, "F2", 15, False, 20))
    righe.append(("", "F1", 6, False, 6))
    for istr in istruzioni:
        for r in _wrap(istr, 9, maxw): righe.append((r, "F1", 9, True, 12))
    righe.append(("", "F1", 6, False, 6)); righe.append(("_" * 95, "F1", 9, True, 16))
    for blocco in lettera.split("\n\n"):
        for riga in blocco.split("\n"):
            bold = riga in ("COMUNICA", "CHIEDE") or riga.startswith("OGGETTO:")
            for r in _wrap(riga, 10.5, maxw, bold): righe.append((r, "F2" if bold else "F1", 10.5, False, 14.5))
        righe.append(("", "F1", 10.5, False, 7))
    pagine, cur, y = [], [], PH - M
    for r in righe:
        if y - r[4] < M: pagine.append(cur); cur, y = [], PH - M
        y -= r[4]; cur.append((r, y))
    pagine.append(cur)
    objs = []
    def add(b): objs.append(b); return len(objs)
    fonts = add(b"")  # placeholder 1 : Resources
    f1 = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    f2 = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    objs[fonts - 1] = f"<< /Font << /F1 {f1} 0 R /F2 {f2} 0 R >> >>".encode()
    pages_id = add(b""); kids = []
    for pg in pagine:
        s = b""
        for (txt, font, size, grigio, _), yy in pg:
            if not txt: continue
            col = b"0.345 0.392 0.478 rg" if grigio else b"0.06 0.106 0.2 rg"
            s += col + f" BT /{font} {size} Tf {M} {yy:.1f} Td (".encode() + _esc(txt) + b") Tj ET\n"
        c = add(f"<< /Length {len(s)} >>\nstream\n".encode() + s + b"endstream")
        kids.append(add(f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PW} {PH}] /Resources {fonts} 0 R /Contents {c} 0 R >>".encode()))
    objs[pages_id - 1] = f"<< /Type /Pages /Kids [{' '.join(f'{k} 0 R' for k in kids)}] /Count {len(kids)} >>".encode()
    info = add(b"<< /Title (" + _esc(titolo) + b") /Producer (disdettaabbonamento.it) >>")
    cat = add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode())
    out = io.BytesIO(); out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"); offs = []
    for i, o in enumerate(objs, 1):
        offs.append(out.tell()); out.write(f"{i} 0 obj\n".encode() + o + b"\nendobj\n")
    x = out.tell()
    out.write(f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode() + b"".join(f"{o:010d} 00000 n \n".encode() for o in offs))
    out.write(f"trailer\n<< /Size {len(objs) + 1} /Root {cat} 0 R /Info {info} 0 R >>\nstartxref\n{x}\n%%EOF\n".encode())
    return out.getvalue()
