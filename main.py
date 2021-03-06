import keras
import snakeML
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import pandas as pd
import geneticAlgo
import math
import tkinter

def updateCanvas(txtbox_id, generation, n_snake, fitness, length):
    scoreScreenCanvas.itemconfig(txtbox_id, text=f"Generation: {generation}, Snake: {n_snake}, Fitness: {fitness}, Length: {length}")
    scoreScreenCanvas.update()


def getPopulationFromCsv():
    df = pd.read_csv("model/generation4.csv", sep=',', header=None)
    return np.asarray(df.values)

#Manually coded. Change it when have time
def reshapeWeights(weights, input_layer_units, hidden_layers_units, output_layer_units):

    firstIndex = 0
    lastIndex = (input_layer_units * hidden_layers_units[0])
    weight_1 = np.reshape(
        weights[firstIndex:lastIndex], (input_layer_units, hidden_layers_units[0]))
    activation_1 = np.zeros(16)  # np.asarray([stackedWeights, np.zeros(9)])
    firstIndex = lastIndex
    lastIndex = firstIndex + (hidden_layers_units[0] * output_layer_units)
    weight_3 = np.reshape(
        weights[firstIndex:lastIndex], (hidden_layers_units[0], output_layer_units))
    activation_3 = np.zeros(4)  # np.asarray([stackedWeights, np.zeros(3)])
    return np.array([weight_1, activation_1, weight_3, activation_3])

def showSnake(modelName):
    model = tf.keras.models.load_model(modelName)
    snakeML.newGameML()
    snakeML.startGameML()
    game_ended = False
    num_steps = 0
    while not game_ended:
        input_layer = snakeML.getInputLayer()
        output = model.predict(np.matrix(input_layer))
        # predict output
        output = np.argmax(output)
        len, game_ended = snakeML.nextStep(output)
        num_steps += 1
    snakeML.exit()


def calcFitness(len, num_steps):
    if len < 10:
        return math.floor(num_steps * num_steps * math.pow(2, math.floor(len)))
    else:
        fitness = num_steps * num_steps
        fitness *= math.pow(2, 10)
        fitness *= (len-9)
        return fitness

#Uncomment following line to see the best performance of a particular generation
#showSnake("model/model_generation_6_best_fitness.h5")
scoreScreenMaster = tkinter.Tk()
scoreScreenCanvas = tkinter.Canvas(
    scoreScreenMaster, bg="white", height=200, width=500)
scoreScreenCanvas.pack()
txtbox_trained_id = scoreScreenCanvas.create_text(250, 20, text=f"Generation: 0, Snake: 0, Fitness: 0, Length: 0")
txtbox_training_id = scoreScreenCanvas.create_text(250, 120, text=f"Generation: 0, Snake: 0, Fitness: training")

GeneticAlgo = geneticAlgo.GeneticAlgo()
num_of_gens = 20
n_population = 2000
max_steps = 2500

# Build model (Building fixed NN first)
input_layer_units = 24
hidden_layers_units = [16]
output_layer_units = 4
model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Dense(
    hidden_layers_units[0], input_dim=input_layer_units, activation=tf.nn.sigmoid))
model.add(tf.keras.layers.Dense(output_layer_units, activation=tf.nn.softmax))
total_weights = input_layer_units * hidden_layers_units[0]
total_weights += hidden_layers_units[0] * output_layer_units

# Genetic loop
population = GeneticAlgo.generatePopulation(
   n_population, total_weights)  # Change to total number of weights
#population = getPopulationFromCsv()
for i in range(1, num_of_gens):
    print(f"Generation {i}:")
    fitness = np.empty(n_population)
    len = np.empty(n_population)
    for j in range(0, n_population):
        weights = reshapeWeights(
            population[j], input_layer_units, hidden_layers_units, output_layer_units)
        model.set_weights(weights)
        snakeML.newGameML()
        snakeML.startGameML(showGui=False)
        game_ended = False
        num_steps = 0
        while not game_ended and (num_steps < max_steps):
            input_layer = snakeML.getInputLayer()
            output = model.predict(np.matrix(input_layer))
            # predict output
            output = np.argmax(output)
            len[j], game_ended = snakeML.nextStep(output)
            num_steps += 1
        fitness[j] = calcFitness(len[j], num_steps)
        snakeML.exit()
        updateCanvas(txtbox_training_id, i, j, fitness[j], len[j])
    best_person = np.argmax(fitness)
    print(f"Generation {i}, Top fitness = {fitness[best_person]}, Length = {len[j]}")
    updateCanvas(txtbox_trained_id, i, "Null", fitness[best_person], len[j])

    weights = reshapeWeights(
        population[best_person], input_layer_units, hidden_layers_units, output_layer_units)
    model.set_weights(weights)
    model.save(f"model/model_generation_{i}_best_fitness.h5")
    print(f"Generation {i} best model saved.")
    print("Creating next generation. This might take a while.")
    population = GeneticAlgo.getNextGeneration(population, fitness)
    df = pd.DataFrame(population)
    df.to_csv(f'model/generation{i+1}.csv', header=None, index=None)
