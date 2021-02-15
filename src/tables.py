import pandas as pd
from df_style import *

def generate_table(df, filename, style):
    pd.set_option("colheader_justify", "center")
    html_string = """
        <html>
          <head><title>HTML Pandas Dataframe with CSS</title></head>
          <link rel="stylesheet" type="text/css" href="style.css"/>
          <body>
            {table}
          </body>
        </html>
        """
    with open("../html/" + filename + ".html", "w") as f:
        f.write(html_string.format(table=df.to_html(classes=style,
                                   index=False)))
