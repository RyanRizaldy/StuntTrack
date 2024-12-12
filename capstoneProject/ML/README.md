# StunTrack : Stunting Detection and Parenting Awareness App Support
blabla

## Requirements
To run this project, you need the following dependencies:
- Python
- TensorFlow
- NumPy
- Pandas
- Scikit-learn
- Flask
- You can install the required packages by running the following command: <code>pip install -r requirements.txt</code>

## Dataset
The dataset used for build model [data_balita_balanced.csv](https://github.com/RyanRizaldy/StuntTrack/blob/main/capstoneProject/ML/dataset/data_balita_balanced.csv) after doing data wrangling in [data_balita.csv](https://github.com/RyanRizaldy/StuntTrack/blob/main/capstoneProject/ML/dataset/data_balita.csv) and doing encoded for features Jenis Kelamin, Status Gizi, and Tinggi Badan [data_balita_encoded.csv](https://github.com/RyanRizaldy/StuntTrack/blob/main/capstoneProject/ML/dataset/data_balita_encoded.csv)

## Usage
1) Clone the repository: <code> git clone https://github.com/RyanRizaldy/StuntTrack.git (https://github.com/RyanRizaldy/StuntTrack.git) </code>
2) Navigate to the project directory: <code>cd ML </code>
3) Prepare your dataset and place it in the appropriate directory.
4) Modify the necessary parameters and settings in <code>main.py</code> and according to your requirements.
5) Run the preprocessing script to prepare your dataset: <code>python</code>. This script will preprocess your data and create the necessary input files for training and evaluation.
6) Run the main training script: <code>python main.py</code>. This script will train the model using the preprocessed data and save the trained model weights.
7) After training, you can evaluate the model using the evaluation script or make predictions on new data.

