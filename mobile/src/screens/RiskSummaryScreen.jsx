import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import MultilingualCard from '../components/MultilingualCard';

export default function RiskSummaryScreen({ result }) {
  if (!result) return null;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.scoreBox}>
        <Text style={styles.scoreLabel}>Contract Safety Score</Text>
        <Text style={styles.scoreValue}>{result.safety_score} / 100</Text>
        <Text style={[styles.riskLevel, { color: result.risk_level === 'RED' ? '#ef4444' : '#f59e0b' }]}>
          {result.risk_level} RISK DETECTED
        </Text>
      </View>

      <Text style={styles.sectionTitle}>Identified Clause Risks</Text>
      {result.findings.map((item, idx) => (
        <MultilingualCard key={idx} finding={item} />
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
    padding: 16,
  },
  scoreBox: {
    backgroundColor: '#0f172a',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#1e293b',
  },
  scoreLabel: {
    color: '#94a3b8',
    fontSize: 12,
  },
  scoreValue: {
    color: '#ffffff',
    fontSize: 32,
    fontWeight: 'bold',
    marginVertical: 4,
  },
  riskLevel: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  sectionTitle: {
    color: '#f8fafc',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
});
