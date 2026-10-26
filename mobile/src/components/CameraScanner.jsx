import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function CameraScanner({ onCapture, isScanning }) {
  return (
    <View style={styles.cameraBox}>
      <Text style={styles.cameraText}>
        {isScanning ? '⚡ Processing OCR & Risk Analysis...' : '📷 Camera Scanner Ready'}
      </Text>
      <Text style={styles.cameraSubtext}>Align paper contract within green border</Text>
      
      <TouchableOpacity 
        style={[styles.captureBtn, isScanning && styles.disabledBtn]} 
        onPress={onCapture}
        disabled={isScanning}
      >
        <Text style={styles.captureBtnText}>
          {isScanning ? 'Analyzing...' : 'Snap & Analyze Contract'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  cameraBox: {
    width: '100%',
    height: 360,
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
    textAlign: 'center',
  },
  cameraSubtext: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 8,
    marginBottom: 20,
  },
  captureBtn: {
    backgroundColor: '#2563eb',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
  },
  disabledBtn: {
    backgroundColor: '#475569',
  },
  captureBtnText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 14,
  },
});
