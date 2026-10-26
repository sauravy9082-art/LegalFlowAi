import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView } from 'react-native';
import CameraScanner from '../components/CameraScanner';

export default function ScanScreen({ onAnalysisComplete }) {
  const [isScanning, setIsScanning] = useState(false);

  const handleCapture = () => {
    setIsScanning(true);
    setTimeout(() => {
      setIsScanning(false);
      if (onAnalysisComplete) {
        onAnalysisComplete({
          safety_score: 55,
          risk_level: 'ORANGE',
          findings: [
            {
              category: 'Security Deposit Forfeiture',
              risk_level: 'HIGH',
              original_text: 'Tenant shall forfeit deposit if lease terminates early.',
              explanation: 'You lose your deposit automatically upon early termination.',
              explanation_hi: 'यह खंड सुरक्षा जमा जब्त करने की अनुमति देता है।',
              explanation_mr: 'हा नियम सुरक्षा ठेव जप्त करण्याची परवानगी देतो.'
            }
          ]
        });
      }
    }, 1500);
  };

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.headerTitle}>LegalFlow Mobile Capture</Text>
      <Text style={styles.headerSubtitle}>Upload contract directly to local Ollama engine</Text>
      <CameraScanner onCapture={handleCapture} isScanning={isScanning} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
    padding: 20,
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 12,
    color: '#94a3b8',
    textAlign: 'center',
    marginBottom: 24,
  },
});
