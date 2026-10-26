import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function MultilingualCard({ finding }) {
  const [lang, setLang] = useState('en');

  const getExplanation = () => {
    if (lang === 'hi') return finding.explanation_hi || finding.explanation;
    if (lang === 'mr') return finding.explanation_mr || finding.explanation;
    return finding.explanation;
  };

  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <Text style={styles.category}>{finding.category}</Text>
        <Text style={[styles.badge, finding.risk_level === 'HIGH' ? styles.redBadge : styles.yellowBadge]}>
          {finding.risk_level}
        </Text>
      </View>
      <Text style={styles.originalText}>"{finding.original_text}"</Text>
      
      <View style={styles.langSelector}>
        {['en', 'hi', 'mr'].map((l) => (
          <TouchableOpacity
            key={l}
            style={[styles.langBtn, lang === l && styles.activeLangBtn]}
            onPress={() => setLang(l)}
          >
            <Text style={[styles.langBtnText, lang === l && styles.activeLangText]}>
              {l === 'en' ? 'English' : l === 'hi' ? 'हिन्दी' : 'मराठी'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      
      <Text style={styles.explanationText}>{getExplanation()}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  category: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#f8fafc',
  },
  badge: {
    fontSize: 10,
    fontWeight: 'bold',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    overflow: 'hidden',
  },
  redBadge: {
    backgroundColor: '#ef4444',
    color: '#ffffff',
  },
  yellowBadge: {
    backgroundColor: '#f59e0b',
    color: '#ffffff',
  },
  originalText: {
    fontSize: 12,
    fontStyle: 'italic',
    color: '#94a3b8',
    marginBottom: 12,
  },
  langSelector: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  langBtn: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
    marginRight: 6,
    backgroundColor: '#334155',
  },
  activeLangBtn: {
    backgroundColor: '#2563eb',
  },
  langBtnText: {
    fontSize: 10,
    color: '#cbd5e1',
  },
  activeLangText: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
  explanationText: {
    fontSize: 13,
    color: '#e2e8f0',
    lineHeight: 18,
  },
});
