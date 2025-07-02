from flask import Flask, render_template, request
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # ✅ Important fix for Flask
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid


app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
df = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global df
    plot_path = None
    columns = []
    numeric_cols = []
    data_preview = None
    error = None

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                df = pd.read_csv(file)
                data_preview = df.head().to_html(classes='table table-bordered', index=False)
                columns = df.columns.tolist()
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        elif df is not None:
            plot_type = request.form.get('plot_type')
            col1 = request.form.get('col1')
            col2 = request.form.get('col2')
            columns = df.columns.tolist()
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            data_preview = df.head().to_html(classes='table table-bordered', index=False)

            try:
                plt.clf()
                if plot_type == 'scatter':
                    plt.scatter(df[col1], df[col2], color='blue')
                    plt.xlabel(col1)
                    plt.ylabel(col2)
                    plt.title(f'Scatter Plot: {col1} vs {col2}')
                elif plot_type == 'hist':
                    plt.hist(df[col1], bins=10, color='green')
                    plt.xlabel(col1)
                    plt.ylabel('Frequency')
                    plt.title(f'Histogram of {col1}')
                elif plot_type == 'bar':
                    df[col1].value_counts().plot(kind='bar', color='orange')
                    plt.xlabel(col1)
                    plt.ylabel('Count')
                    plt.title(f'Bar Plot of {col1}')
                elif plot_type == 'pie':
                    counts = df[col1].value_counts()
                    plt.pie(counts, labels=counts.index, autopct='%1.1f%%')
                    plt.title(f'Pie Chart of {col1}')
                elif plot_type == 'heat':
                    corr = df[numeric_cols].corr()
                    plt.figure(figsize=(10, 8))
                    sns.heatmap(corr, annot=True, cmap='coolwarm')
                    plt.title('Heatmap')
                elif plot_type == 'line':
                    plt.plot(df[col1], df[col2], color='purple')
                    plt.xlabel(col1)
                    plt.ylabel(col2)
                    plt.title(f'Line Graph: {col1} vs {col2}')
                filename = f"{uuid.uuid4().hex}.png"
                plot_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                plt.savefig(plot_path)
                plot_path = '/' + plot_path
            except Exception as e:
                error = f"❌ An error occurred: {e}"

    return render_template('index.html', columns=columns, numeric=numeric_cols,
                           preview=data_preview, plot=plot_path, error=error)

if __name__ == '__main__':
    app.run(debug=True)
