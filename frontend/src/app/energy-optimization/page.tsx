'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  BatteryIcon,
  ZapIcon,
  TrendingDownIcon,
  ActivityIcon,
  ThermometerIcon,
  WindIcon,
  AlertTriangleIcon,
  DatabaseIcon,
  ServerIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  DollarSignIcon,
  LeafIcon,
  LockIcon,
  XCircleIcon
} from 'lucide-react';

const EnergyOptimizationPage = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const potentialCapabilities = [
    {
      icon: ZapIcon,
      title: 'Ottimizzazione Energetica Real-time',
      description: 'Riduzione del consumo energetico fino al 30% attraverso algoritmi AI',
      requirements: ['Dati telemetria pompe', 'Misuratori di consumo', 'API SCADA'],
      potentialSavings: '€200.000/anno'
    },
    {
      icon: WindIcon,
      title: 'Gestione Inerzia Idraulica',
      description: "Sfruttamento dell'inerzia del sistema per ridurre i picchi di consumo",
      requirements: ['Sensori di pressione', 'Dati portata real-time', 'Controllo VSD pompe'],
      potentialSavings: '€85.000/anno'
    },
    {
      icon: ThermometerIcon,
      title: 'Recupero Energia Termica',
      description: 'Harvesting energetico da espansioni termiche delle condotte',
      requirements: ['Sensori temperatura', 'Dati materiali condotte', 'Sensori dilatazione'],
      potentialSavings: '€45.000/anno'
    },
    {
      icon: DollarSignIcon,
      title: 'Scheduling Intelligente',
      description: 'Ottimizzazione oraria basata su tariffe energetiche variabili',
      requirements: ['Tariffe energetiche real-time', 'Dati storici consumi', 'Previsioni domanda'],
      potentialSavings: '€120.000/anno'
    },
    {
      icon: LeafIcon,
      title: 'Monitoraggio Impatto Ambientale',
      description: 'Tracking CO₂ risparmiata e certificazioni green',
      requirements: ['Fattori emissione energia', 'Baseline consumi', 'Dati produzione'],
      potentialSavings: '500 ton CO₂/anno'
    },
    {
      icon: ActivityIcon,
      title: 'Analisi Predittiva',
      description: 'Previsione guasti e ottimizzazione manutenzione preventiva',
      requirements: ['Storico guasti', 'Parametri vibrazione', 'Ore di funzionamento'],
      potentialSavings: '€150.000/anno'
    }
  ];

  const missingDataSources = [
    { name: 'SCADA System', status: 'Non Connesso', critical: true, description: 'Sistema di controllo e acquisizione dati' },
    { name: 'Telemetria Pompe', status: 'Non Disponibile', critical: true, description: 'Dati real-time pompe e motori' },
    { name: 'Sensori Pressione', status: 'Non Integrati', critical: true, description: 'Monitoraggio pressione rete' },
    { name: 'Misuratori Portata', status: 'Dati Parziali', critical: false, description: 'Flussi idrici in tempo reale' },
    { name: 'Database Consumi', status: 'Non Accessibile', critical: true, description: 'Storico consumi energetici' },
    { name: 'API Tariffe Energia', status: 'Non Configurata', critical: false, description: 'Prezzi energia in tempo reale' }
  ];

  const potentialBenefits = [
    { metric: 'Risparmio Energetico Annuale', value: '€600.000+', icon: DollarSignIcon, color: 'green' },
    { metric: 'Riduzione Emissioni CO₂', value: '500+ ton/anno', icon: LeafIcon, color: 'emerald' },
    { metric: 'ROI Stimato', value: '< 2 anni', icon: TrendingDownIcon, color: 'blue' },
    { metric: 'Efficienza Sistema', value: '+35%', icon: ActivityIcon, color: 'purple' }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Critical Alert */}
      <div className="mb-6 p-6 bg-red-50 dark:bg-red-900/20 border-2 border-red-300 dark:border-red-800 rounded-lg">
        <div className="flex items-start gap-4">
          <AlertTriangleIcon className="h-8 w-8 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="font-bold text-red-900 dark:text-red-100 mb-3 text-xl">
              Sistema di Ottimizzazione Non Operativo - Dati Non Disponibili
            </h3>
            <p className="text-red-800 dark:text-red-200 mb-4 font-medium">
              Abbiamo sviluppato un sistema avanzato di ottimizzazione energetica che potrebbe generare risparmi superiori a €600.000/anno, 
              ma <span className="font-bold underline">non possiamo attivarlo senza accesso ai vostri dati operativi</span>.
            </p>
            <div className="bg-white dark:bg-gray-900 p-4 rounded-lg border border-red-200 dark:border-red-700">
              <p className="text-gray-700 dark:text-gray-300 text-sm mb-2">
                <strong>Cosa stiamo perdendo ogni giorno senza questi dati:</strong>
              </p>
              <ul className="text-sm space-y-1 text-gray-600 dark:text-gray-400">
                <li>• €1.650 di risparmio energetico giornaliero</li>
                <li>• 1.4 tonnellate di CO₂ che potrebbero essere evitate</li>
                <li>• Capacità di prevenire guasti costosi prima che accadano</li>
                <li>• Opportunità di certificazioni ambientali e incentivi</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-3">
              <BatteryIcon className="h-8 w-8 text-gray-400" />
              Centro Ottimizzazione Energetica
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Potenzialità del sistema AI per la gestione energetica sostenibile
            </p>
          </div>
          <div className="flex gap-4">
            <Button variant="secondary" disabled className="flex items-center gap-2 opacity-50">
              <LockIcon className="h-4 w-4" />
              Sistema Bloccato
            </Button>
          </div>
        </div>
      </div>

      {/* Potential Benefits */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {potentialBenefits.map((benefit, idx) => {
          const Icon = benefit.icon;
          return (
            <Card key={idx} className="p-4 bg-gray-50 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 opacity-75">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{benefit.metric}</p>
                  <p className="text-2xl font-bold text-gray-400">
                    {benefit.value}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    (Non disponibile)
                  </p>
                </div>
                <Icon className={`h-8 w-8 text-gray-400 opacity-50`} />
              </div>
            </Card>
          );
        })}
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
        {['overview', 'requirements', 'capabilities'].map((tab) => (
          <button
            key={tab}
            className={`pb-3 px-1 ${
              activeTab === tab
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'overview' && 'Panoramica'}
            {tab === 'requirements' && 'Requisiti Dati'}
            {tab === 'capabilities' && 'Capacità Sistema'}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* What We Could Do */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <ZapIcon className="h-6 w-6 text-yellow-500" />
              Cosa Potremmo Fare Con i Vostri Dati
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {potentialCapabilities.map((capability, idx) => {
                const Icon = capability.icon;
                return (
                  <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div className="flex items-start gap-3">
                      <Icon className="h-6 w-6 text-blue-500 mt-1 flex-shrink-0" />
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                          {capability.title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          {capability.description}
                        </p>
                        <div className="flex items-center gap-2 text-green-600 font-medium text-sm">
                          <ArrowRightIcon className="h-4 w-4" />
                          Risparmio potenziale: {capability.potentialSavings}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* ROI Calculator */}
          <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
            <h2 className="text-xl font-semibold mb-4">Calcolo ROI Potenziale</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">€600.000+</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Risparmio Annuale Stimato</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">&lt; 24 mesi</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Tempo di Recupero Investimento</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-purple-600">€3M+</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Valore Generato in 5 Anni</p>
              </div>
            </div>
            <div className="mt-6 p-4 bg-white dark:bg-gray-900 rounded-lg">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>Nota:</strong> Questi valori sono stime conservative basate su implementazioni simili. 
                I risparmi effettivi potrebbero essere significativamente superiori con l'ottimizzazione completa del sistema.
              </p>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'requirements' && (
        <div className="space-y-6">
          {/* Missing Data Sources */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <DatabaseIcon className="h-6 w-6 text-red-500" />
              Sorgenti Dati Necessarie (Attualmente Non Disponibili)
            </h2>
            <div className="space-y-3">
              {missingDataSources.map((source, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-2 ${
                    source.critical
                      ? 'border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
                      : 'border-yellow-300 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <XCircleIcon className={`h-5 w-5 ${source.critical ? 'text-red-600' : 'text-yellow-600'}`} />
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100">{source.name}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{source.description}</p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      source.critical
                        ? 'bg-red-200 text-red-800 dark:bg-red-800 dark:text-red-200'
                        : 'bg-yellow-200 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200'
                    }`}>
                      {source.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Integration Steps */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Passi per l'Integrazione</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">1</div>
                <div>
                  <h3 className="font-semibold">Connessione SCADA</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Fornire accesso read-only ai sistemi SCADA per acquisizione dati real-time
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">2</div>
                <div>
                  <h3 className="font-semibold">API Telemetria</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Configurare endpoint API per ricevere dati da sensori e misuratori
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">3</div>
                <div>
                  <h3 className="font-semibold">Database Storici</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Accesso ai dati storici per training modelli AI (minimo 12 mesi)
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">4</div>
                <div>
                  <h3 className="font-semibold">Validazione e Testing</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Periodo di validazione di 30 giorni per calibrazione algoritmi
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'capabilities' && (
        <div className="space-y-6">
          {/* Detailed Capabilities */}
          {potentialCapabilities.map((capability, idx) => {
            const Icon = capability.icon;
            return (
              <Card key={idx} className="p-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                    <Icon className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold mb-2">{capability.title}</h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">{capability.description}</p>
                    
                    <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg mb-4">
                      <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300 mb-2">
                        Dati Necessari per Attivazione:
                      </h4>
                      <ul className="space-y-1">
                        {capability.requirements.map((req, reqIdx) => (
                          <li key={reqIdx} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <XCircleIcon className="h-4 w-4 text-red-500" />
                            {req}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-500">Risparmio Potenziale:</span>
                        <span className="font-bold text-green-600 text-lg">{capability.potentialSavings}</span>
                      </div>
                      <Button variant="secondary" disabled className="opacity-50">
                        <LockIcon className="h-4 w-4 mr-2" />
                        Richiede Dati
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}

          {/* Call to Action */}
          <Card className="p-8 bg-gradient-to-r from-blue-600 to-blue-700 text-white">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-4">
                Pronti ad Attivare il Risparmio Energetico?
              </h2>
              <p className="mb-6 text-blue-100">
                Contattateci per discutere l'integrazione dei vostri sistemi e iniziare a risparmiare.
                Il nostro team è pronto a supportarvi in ogni fase del processo.
              </p>
              <div className="flex gap-4 justify-center">
                <Button variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100">
                  Richiedi Demo Personalizzata
                </Button>
                <Button variant="ghost" className="text-white border-white hover:bg-blue-600">
                  Scarica Documentazione Tecnica
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default EnergyOptimizationPage;