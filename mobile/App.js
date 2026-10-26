import React from 'react';
import { StyleSheet, Text, View, TouchableOpacity, SafeAreaView, StatusBar } from 'react-native';

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#020617" />
      <View style={styles.header}>
        <Text style={styles.title}>LegalFlow Mobile Scanner</Text>
        <Text style={styles.subtitle}>Air-Gapped Mobile Document Capture</Text>
      </View>
      <View style={styles.cameraBox}>
        <Text style={styles.cameraText}>[ Camera Viewfinder Ready ]</Text>
        <Text style={styles.cameraSubtext}>Align paper contract within green border</Text>
      </View>
      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>Capture & Upload to Desktop AI Engine</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  header: {
    alignItems: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  subtitle: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 4,
  },
  cameraBox: {
    width: '100%',
    height: 380,
    backgroundColor: '#0f172a',
    borderRadius: 20,
    borderWidth: 2,
    borderColor: '#22c55e',
    borderStyle: 'dashed',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  cameraText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4ade80',
  },
  cameraSubtext: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 8,
  },
  button: {
    width: '100%',
    backgroundColor: '#2563eb',
    paddingVertical: 16,
    borderRadius: 14,
    alignItems: 'center',
  },
  buttonText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 14,
  },
});
