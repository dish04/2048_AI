🎮 **2048 AI with NEAT** 🧠

This project implements an AI player for the popular game 2048 using NEAT (NeuroEvolution of Augmenting Topologies), a genetic algorithm for evolving artificial neural networks. Watch as the AI learns to play and achieve high scores in the game!

### Features:
- **NEAT Implementation**: Utilizes NEAT algorithm to evolve neural networks that play 2048.
- **Customizable Parameters**: Easily tweak NEAT parameters such as population size, mutation rates, and fitness thresholds.
- **Visualization**: Visualize the progress of the AI learning process and neural network architectures.
- **Game Integration**: Seamless integration with the 2048 game environment for training and testing.

### How it works:
1. **Initialization**: Initially, a population of neural networks with random weights and structures is created.
2. **Evaluation**: Each neural network plays the game independently, and their performance is evaluated based on the achieved score.
3. **Selection**: Neural networks are selected for reproduction based on their performance (fitness).
4. **Crossover and Mutation**: Reproduction involves crossover and mutation to produce offspring with slightly modified neural structures and weights.
5. **Next Generation**: The new generation replaces the old one, and the process iterates until the AI improves its performance over generations.
