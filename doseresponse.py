def hill_equation(x, a, b, c, d):
    y = a + (b-a)/(1+(c/x)**d)
    return y

def dose_response(df, title):
    """ 
    Dataframe should be in the format rows = concentrations, columns = replicates
    The first row sould be the control
    
    """
    from bokeh.plotting import figure
    import numpy as np
    import math
    from bokeh.models import FixedTicker
    
    from scipy.optimize import curve_fit
    color ='blue'
    alpha = 0.6
    control = df.iloc[0, :]
    tests = df.iloc[1:, :]

    points = (tests / control.mean() * 100).mean(1)
    std = (tests / control.mean() * 100).std(1)
    err_y = list(zip(points + std, points - std))
    
    x_labels = list(points.index)
    f = figure(title=title)
    f.circle(x=x_labels, y=points.values, color=color, alpha=alpha)
    f.multi_line(xs=list(zip(x_labels, x_labels)), 
                 ys=err_y, color=color, alpha=alpha)

    popt, pcov = curve_fit(hill_equation, 
                           tests.index.astype(float).tolist(), 
                           (tests / control.mean() * 100).mean(1).values
                          )
    

    x = np.linspace(tests.index.astype(float).max(), tests.index.astype(float).min(), num=5000)
    y = hill_equation(x, *popt)

    f.line(x, y, color=color, alpha=alpha, line_dash='dashed')
    
    
    x_labels = tests.index.astype(float).tolist()
    
    f.xaxis.ticker=FixedTicker(ticks=sorted(x_labels))
    f.xaxis.axis_label = "Concentration (uM)"
    f.yaxis.axis_label = "% cells remaining relative to control"
    f.title.text_font_size = "16pt"

    #lc50 = popt[2]
    #f.cross(lc50, 50, color='red', legend='LC50')
    return f

if __name__ == "__main__":
	import argparse
	import pandas as pd
	from bokeh.plotting import output_file, show
	parser = argparse.ArgumentParser(description='Will create a dose response curve from a plate reader file')
	parser.add_argument('filename', metavar='F', type=str,
                        help='the filename of the smiles.txt file')
	parser.add_argument("-d", "--display", help="display the plot", action="store_true")

	args = parser.parse_args()

	df = pd.read_table(args.filename, index_col=0)
	plot = dose_response(df, args.filename[:-4])
	output_file(args.filename[:-4]+'.html')
	if args.display:
		show(plot)
