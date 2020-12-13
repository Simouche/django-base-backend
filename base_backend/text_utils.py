def trim_text_to_90chars(text: str) -> list:
    """
    needed that in one of my projects where i had to trim the length of a line in a pdf to 90chars,
     it may inspire someone with the same issue.
    """
    words = text.split()
    a_line = ""
    lines = []
    for word in words:
        if word == "Paragraphe" or word == "paragraphe":
            lines.append(a_line)
            a_line = ""
        elif (len(a_line) + len(word)) < 90:
            a_line += " " + word
        else:
            lines.append(a_line)
            a_line = " " + word
    lines.append(a_line)
    return lines
