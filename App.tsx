import React, { useState } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';

export default function App() {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);

  const options = [
    'Shade',
    'Dooring Risk',
    'Less Traffic',
    'Dedicated Cycling',
  ];

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Select Your Preference</Text>

      {options.map((option) => (
        <TouchableOpacity
          key={option}
          style={[
            styles.button,
            selectedOption === option && styles.selectedButton,
          ]}
          onPress={() => setSelectedOption(option)}
        >
          <Text
            style={[
              styles.buttonText,
              selectedOption === option && styles.selectedButtonText,
            ]}
          >
            {option}
          </Text>
        </TouchableOpacity>
      ))}

      {selectedOption && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultText}>
            Selected: {selectedOption}
          </Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
  },
  button: {
    backgroundColor: '#e5e7eb',
    padding: 16,
    borderRadius: 10,
    marginBottom: 12,
  },
  selectedButton: {
    backgroundColor: '#2563eb',
  },
  buttonText: {
    textAlign: 'center',
    fontSize: 16,
    color: '#000000',
  },
  selectedButtonText: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
  resultContainer: {
    marginTop: 30,
    alignItems: 'center',
  },
  resultText: {
    fontSize: 18,
    fontWeight: '600',
  },
});