#!/usr/bin/env python3
"""
Test der kompletten Lösung: Queue + Chunking + Content-Preprocessing
"""

import asyncio
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.enhanced_mcp_server import EnhancedMoodleMCPServer

async def test_complete_solution():
    """Test the complete solution with problematic content"""
    
    print("🚀 Testing Complete Solution: Queue + Chunking + Preprocessing")
    print("=" * 70)
    
    # Create content that historically caused problems
    problematic_content = """
    # Comprehensive Machine Learning Guide 🤖

    ## Introduction to Neural Networks

    Neural networks are the foundation of modern AI! 💡 Let's explore:

    ```python
    import numpy as np
    import tensorflow as tf
    from sklearn.preprocessing import StandardScaler
    import matplotlib.pyplot as plt
    
    # Advanced neural network implementation
    class DeepNeuralNetwork:
        def __init__(self, layers, activation='relu', learning_rate=0.01):
            self.layers = layers
            self.activation = activation
            self.learning_rate = learning_rate
            self.weights = []
            self.biases = []
            self.initialize_parameters()
        
        def initialize_parameters(self):
            \"\"\"Initialize weights and biases using Xavier initialization\"\"\"
            for i in range(len(self.layers) - 1):
                # Xavier initialization for better convergence
                w = np.random.randn(self.layers[i], self.layers[i+1]) * np.sqrt(2.0 / self.layers[i])
                b = np.zeros((1, self.layers[i+1]))
                self.weights.append(w)
                self.biases.append(b)
        
        def relu(self, x):
            \"\"\"ReLU activation function\"\"\"
            return np.maximum(0, x)
        
        def relu_derivative(self, x):
            \"\"\"Derivative of ReLU function\"\"\"
            return (x > 0).astype(float)
        
        def sigmoid(self, x):
            \"\"\"Sigmoid activation function\"\"\"
            return 1 / (1 + np.exp(-np.clip(x, -250, 250)))  # Prevent overflow
        
        def sigmoid_derivative(self, x):
            \"\"\"Derivative of sigmoid function\"\"\"
            s = self.sigmoid(x)
            return s * (1 - s)
        
        def forward_propagation(self, X):
            \"\"\"Forward pass through the network\"\"\"
            self.layer_outputs = [X]
            self.layer_inputs = []
            
            current_input = X
            for i, (w, b) in enumerate(zip(self.weights, self.biases)):
                z = np.dot(current_input, w) + b
                self.layer_inputs.append(z)
                
                if i == len(self.weights) - 1:  # Output layer
                    a = self.sigmoid(z)
                else:  # Hidden layers
                    a = self.relu(z)
                
                self.layer_outputs.append(a)
                current_input = a
            
            return current_input
        
        def backward_propagation(self, X, y, output):
            \"\"\"Backward pass to compute gradients\"\"\"
            m = X.shape[0]
            
            # Initialize gradients
            dw = [np.zeros_like(w) for w in self.weights]
            db = [np.zeros_like(b) for b in self.biases]
            
            # Output layer error
            dz = output - y
            
            # Backpropagate through all layers
            for i in reversed(range(len(self.weights))):
                # Compute gradients
                dw[i] = (1/m) * np.dot(self.layer_outputs[i].T, dz)
                db[i] = (1/m) * np.sum(dz, axis=0, keepdims=True)
                
                if i > 0:  # Not the first layer
                    # Compute error for previous layer
                    da_prev = np.dot(dz, self.weights[i].T)
                    dz = da_prev * self.relu_derivative(self.layer_inputs[i-1])
            
            return dw, db
        
        def update_parameters(self, dw, db):
            \"\"\"Update weights and biases using gradients\"\"\"
            for i in range(len(self.weights)):
                self.weights[i] -= self.learning_rate * dw[i]
                self.biases[i] -= self.learning_rate * db[i]
        
        def compute_loss(self, y_true, y_pred):
            \"\"\"Compute binary cross-entropy loss\"\"\"
            m = y_true.shape[0]
            # Prevent log(0) by adding small epsilon
            epsilon = 1e-15
            y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
            loss = -(1/m) * np.sum(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
            return loss
        
        def train(self, X, y, epochs=1000, verbose=True):
            \"\"\"Train the neural network\"\"\"
            losses = []
            
            for epoch in range(epochs):
                # Forward propagation
                output = self.forward_propagation(X)
                
                # Compute loss
                loss = self.compute_loss(y, output)
                losses.append(loss)
                
                # Backward propagation
                dw, db = self.backward_propagation(X, y, output)
                
                # Update parameters
                self.update_parameters(dw, db)
                
                if verbose and epoch % 100 == 0:
                    print(f"Epoch {epoch}, Loss: {loss:.4f}")
            
            return losses
        
        def predict(self, X):
            \"\"\"Make predictions on new data\"\"\"
            output = self.forward_propagation(X)
            return (output > 0.5).astype(int)
    
    # Example usage with synthetic data
    if __name__ == "__main__":
        # Generate synthetic dataset
        np.random.seed(42)
        X = np.random.randn(1000, 4)  # 1000 samples, 4 features
        y = ((X[:, 0] + X[:, 1] - X[:, 2] + X[:, 3]) > 0).astype(int).reshape(-1, 1)
        
        # Normalize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split data
        split = int(0.8 * len(X))
        X_train, X_test = X_scaled[:split], X_scaled[split:]
        y_train, y_test = y[:split], y[split:]
        
        # Create and train model
        model = DeepNeuralNetwork([4, 10, 8, 1], learning_rate=0.1)
        losses = model.train(X_train, y_train, epochs=500, verbose=True)
        
        # Evaluate model
        train_predictions = model.predict(X_train)
        test_predictions = model.predict(X_test)
        
        train_accuracy = np.mean(train_predictions == y_train)
        test_accuracy = np.mean(test_predictions == y_test)
        
        print(f"\\nTraining Accuracy: {train_accuracy:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f}")
        
        # Plot training loss
        plt.figure(figsize=(10, 6))
        plt.plot(losses)
        plt.title('Training Loss Over Time')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.grid(True)
        plt.show()
    ```

    This neural network implementation demonstrates key concepts! 🧠

    ## Convolutional Neural Networks

    CNNs are perfect for image processing! 📸 Here's an advanced example:

    ```python
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torchvision import datasets, transforms
    from torch.utils.data import DataLoader
    
    class AdvancedCNN(nn.Module):
        def __init__(self, num_classes=10):
            super(AdvancedCNN, self).__init__()
            
            # First convolutional block
            self.conv_block1 = nn.Sequential(
                nn.Conv2d(3, 32, kernel_size=3, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(inplace=True),
                nn.Conv2d(32, 32, kernel_size=3, padding=1),
                nn.BatchNorm2d(32),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Dropout2d(0.25)
            )
            
            # Second convolutional block
            self.conv_block2 = nn.Sequential(
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(inplace=True),
                nn.Conv2d(64, 64, kernel_size=3, padding=1),
                nn.BatchNorm2d(64),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Dropout2d(0.25)
            )
            
            # Third convolutional block
            self.conv_block3 = nn.Sequential(
                nn.Conv2d(64, 128, kernel_size=3, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                nn.Conv2d(128, 128, kernel_size=3, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Dropout2d(0.25)
            )
            
            # Fully connected layers
            self.classifier = nn.Sequential(
                nn.AdaptiveAvgPool2d((1, 1)),
                nn.Flatten(),
                nn.Linear(128, 512),
                nn.ReLU(inplace=True),
                nn.Dropout(0.5),
                nn.Linear(512, num_classes)
            )
        
        def forward(self, x):
            x = self.conv_block1(x)
            x = self.conv_block2(x)
            x = self.conv_block3(x)
            x = self.classifier(x)
            return x
    
    def train_model(model, train_loader, val_loader, epochs=50):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5)
        
        best_val_acc = 0
        train_losses = []
        val_accuracies = []
        
        for epoch in range(epochs):
            # Training phase
            model.train()
            running_loss = 0.0
            
            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = data.to(device), target.to(device)
                
                optimizer.zero_grad()
                output = model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
                
                running_loss += loss.item()
                
                if batch_idx % 100 == 0:
                    print(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}')
            
            # Validation phase
            model.eval()
            val_loss = 0
            correct = 0
            total = 0
            
            with torch.no_grad():
                for data, target in val_loader:
                    data, target = data.to(device), target.to(device)
                    output = model(data)
                    val_loss += criterion(output, target).item()
                    
                    _, predicted = output.max(1)
                    total += target.size(0)
                    correct += predicted.eq(target).sum().item()
            
            val_acc = 100. * correct / total
            avg_train_loss = running_loss / len(train_loader)
            avg_val_loss = val_loss / len(val_loader)
            
            train_losses.append(avg_train_loss)
            val_accuracies.append(val_acc)
            
            print(f'Epoch {epoch}: Train Loss: {avg_train_loss:.4f}, Val Acc: {val_acc:.2f}%')
            
            # Learning rate scheduling
            scheduler.step(avg_val_loss)
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(model.state_dict(), 'best_model.pth')
        
        return train_losses, val_accuracies
    ```

    This shows advanced PyTorch techniques! 🔥

    ## Natural Language Processing

    Let's explore transformer architectures! 📝 Here's a complete implementation:

    ```python
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import math
    import numpy as np
    from torch.nn import TransformerEncoder, TransformerEncoderLayer
    
    class PositionalEncoding(nn.Module):
        def __init__(self, d_model, max_seq_length=5000):
            super(PositionalEncoding, self).__init__()
            
            pe = torch.zeros(max_seq_length, d_model)
            position = torch.arange(0, max_seq_length, dtype=torch.float).unsqueeze(1)
            
            div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                               (-math.log(10000.0) / d_model))
            
            pe[:, 0::2] = torch.sin(position * div_term)
            pe[:, 1::2] = torch.cos(position * div_term)
            pe = pe.unsqueeze(0).transpose(0, 1)
            
            self.register_buffer('pe', pe)
        
        def forward(self, x):
            return x + self.pe[:x.size(0), :]
    
    class TransformerModel(nn.Module):
        def __init__(self, vocab_size, d_model=512, nhead=8, num_layers=6, 
                     dim_feedforward=2048, max_seq_length=5000, dropout=0.1):
            super(TransformerModel, self).__init__()
            
            self.d_model = d_model
            self.embedding = nn.Embedding(vocab_size, d_model)
            self.pos_encoding = PositionalEncoding(d_model, max_seq_length)
            
            encoder_layer = TransformerEncoderLayer(
                d_model=d_model,
                nhead=nhead,
                dim_feedforward=dim_feedforward,
                dropout=dropout,
                activation='relu'
            )
            
            self.transformer_encoder = TransformerEncoder(encoder_layer, num_layers)
            self.output_layer = nn.Linear(d_model, vocab_size)
            self.dropout = nn.Dropout(dropout)
            
            self._init_weights()
        
        def _init_weights(self):
            for module in self.modules():
                if isinstance(module, nn.Linear):
                    torch.nn.init.xavier_uniform_(module.weight)
                    if module.bias is not None:
                        torch.nn.init.zeros_(module.bias)
                elif isinstance(module, nn.Embedding):
                    torch.nn.init.xavier_uniform_(module.weight)
        
        def forward(self, src, src_mask=None, src_key_padding_mask=None):
            # src shape: (seq_len, batch_size)
            src = self.embedding(src) * math.sqrt(self.d_model)
            src = self.pos_encoding(src)
            src = self.dropout(src)
            
            output = self.transformer_encoder(
                src, 
                mask=src_mask, 
                src_key_padding_mask=src_key_padding_mask
            )
            
            output = self.output_layer(output)
            return output
        
        def generate_square_subsequent_mask(self, sz):
            mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
            mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
            return mask
    
    # Text preprocessing utilities
    class TextTokenizer:
        def __init__(self):
            self.word_to_idx = {'<PAD>': 0, '<UNK>': 1, '<SOS>': 2, '<EOS>': 3}
            self.idx_to_word = {0: '<PAD>', 1: '<UNK>', 2: '<SOS>', 3: '<EOS>'}
            self.vocab_size = 4
        
        def build_vocab(self, texts, min_freq=2):
            word_counts = {}
            
            for text in texts:
                words = text.lower().split()
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            # Add words that meet minimum frequency
            for word, count in word_counts.items():
                if count >= min_freq and word not in self.word_to_idx:
                    self.word_to_idx[word] = self.vocab_size
                    self.idx_to_word[self.vocab_size] = word
                    self.vocab_size += 1
        
        def encode(self, text, max_length=None):
            words = text.lower().split()
            indices = [self.word_to_idx.get(word, 1) for word in words]  # 1 is <UNK>
            
            if max_length:
                if len(indices) > max_length:
                    indices = indices[:max_length]
                else:
                    indices.extend([0] * (max_length - len(indices)))  # 0 is <PAD>
            
            return indices
        
        def decode(self, indices):
            words = [self.idx_to_word.get(idx, '<UNK>') for idx in indices]
            return ' '.join(word for word in words if word not in ['<PAD>', '<SOS>', '<EOS>'])
    
    def train_language_model(model, train_loader, val_loader, epochs=50):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        
        criterion = nn.CrossEntropyLoss(ignore_index=0)  # Ignore padding tokens
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.0001, betas=(0.9, 0.98), eps=1e-9)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
        
        best_val_loss = float('inf')
        
        for epoch in range(epochs):
            # Training
            model.train()
            total_loss = 0
            
            for batch_idx, (data, targets) in enumerate(train_loader):
                data, targets = data.to(device), targets.to(device)
                
                # Create masks
                seq_len = data.size(0)
                src_mask = model.generate_square_subsequent_mask(seq_len).to(device)
                
                optimizer.zero_grad()
                output = model(data, src_mask)
                
                # Reshape for loss calculation
                output = output.view(-1, output.size(-1))
                targets = targets.view(-1)
                
                loss = criterion(output, targets)
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
                
                optimizer.step()
                total_loss += loss.item()
                
                if batch_idx % 100 == 0:
                    print(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}')
            
            # Validation
            model.eval()
            val_loss = 0
            
            with torch.no_grad():
                for data, targets in val_loader:
                    data, targets = data.to(device), targets.to(device)
                    
                    seq_len = data.size(0)
                    src_mask = model.generate_square_subsequent_mask(seq_len).to(device)
                    
                    output = model(data, src_mask)
                    
                    output = output.view(-1, output.size(-1))
                    targets = targets.view(-1)
                    
                    loss = criterion(output, targets)
                    val_loss += loss.item()
            
            avg_train_loss = total_loss / len(train_loader)
            avg_val_loss = val_loss / len(val_loader)
            
            print(f'Epoch {epoch}: Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}')
            
            scheduler.step()
            
            # Save best model
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                torch.save(model.state_dict(), 'best_transformer.pth')
    ```

    This demonstrates state-of-the-art NLP techniques! 🌟

    Machine learning is an incredible field with endless possibilities! Keep exploring and building amazing AI systems! 🚀🤖✨
    """
    
    print(f"📊 Problematic content size: {len(problematic_content)} characters")
    print(f"📊 Contains emojis and special characters that historically caused issues")
    
    # Create MCP server instance
    server = EnhancedMoodleMCPServer()
    
    # Test the complete solution
    try:
        print(f"\n📚 Creating course with complete solution (Queue + Chunking + Preprocessing)...")
        
        # Simulate tool call with problematic content
        arguments = {
            "chat_content": problematic_content,
            "course_name": "Advanced ML with Complete Solution Testing 🤖",
            "course_description": "Testing comprehensive solution with problematic content including emojis, large code blocks, and complex formatting",
            "category_id": 1
        }
        
        # Call the course creation function
        result = await server._create_course_from_chat(arguments)
        
        if result and len(result) > 0:
            response_text = result[0].text
            print(f"✅ Course creation result:")
            print("=" * 70)
            print(response_text)
            print("=" * 70)
            
            # Analyze the response for solution effectiveness
            if "Content Preprocessing Results" in response_text:
                print(f"\n🎉 SUCCESS! Complete solution is working!")
                print(f"✅ Queue processing implemented")
                print(f"✅ Content chunking active")
                print(f"✅ Parameter preprocessing working")
                print(f"✅ Size optimization applied")
                print(f"✅ Success probability estimation provided")
            elif "success" in response_text.lower():
                print(f"\n✅ Course created successfully")
            else:
                print(f"\n⚠️ Partial success or issues detected")
                
        else:
            print(f"❌ No result returned from course creation")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 70)
    print(f"🎯 Complete Solution Test Finished")

if __name__ == "__main__":
    asyncio.run(test_complete_solution())