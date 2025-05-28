import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, ScrollView } from 'react-native';
import axios from 'axios';

const Stack = createNativeStackNavigator();

interface MCPResponse {
  response: {
    flight_info: any;
    query: string;
  };
  context: {
    last_query: string;
    last_flight: string;
    timestamp: string;
  };
  status: string;
}

function HomeScreen({ navigation }) {
  const [flightNumber, setFlightNumber] = React.useState('');
  const [flightInfo, setFlightInfo] = React.useState<MCPResponse | null>(null);
  const [context, setContext] = React.useState<any>({});

  const searchFlight = async () => {
    try {
      const response = await axios.post('http://localhost:8000/mcp/query', {
        context: context,
        query: `Get information for flight ${flightNumber}`,
        parameters: {
          flight_iata: flightNumber
        }
      });
      
      setFlightInfo(response.data);
      setContext(response.data.context);
    } catch (error) {
      console.error('Error fetching flight info:', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>TransportAI</Text>
        <TextInput
          style={styles.input}
          placeholder="Enter Flight Number (e.g., TK123)"
          value={flightNumber}
          onChangeText={setFlightNumber}
        />
        <TouchableOpacity style={styles.button} onPress={searchFlight}>
          <Text style={styles.buttonText}>Search Flight</Text>
        </TouchableOpacity>
        
        {flightInfo && (
          <View style={styles.resultContainer}>
            <Text style={styles.resultTitle}>Flight Information:</Text>
            <Text style={styles.contextInfo}>
              Last Query: {flightInfo.context.last_query}
            </Text>
            <Text style={styles.contextInfo}>
              Last Flight: {flightInfo.context.last_flight}
            </Text>
            <Text style={styles.contextInfo}>
              Timestamp: {flightInfo.context.timestamp}
            </Text>
            <Text style={styles.flightInfo}>
              {JSON.stringify(flightInfo.response.flight_info, null, 2)}
            </Text>
          </View>
        )}
        <StatusBar style="auto" />
      </View>
    </ScrollView>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen 
          name="Home" 
          component={HomeScreen} 
          options={{ title: 'TransportAI' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  input: {
    width: '100%',
    height: 40,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    paddingHorizontal: 10,
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 5,
    width: '100%',
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  resultContainer: {
    marginTop: 20,
    padding: 15,
    backgroundColor: '#f5f5f5',
    borderRadius: 5,
    width: '100%',
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  contextInfo: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  flightInfo: {
    marginTop: 10,
    fontSize: 14,
  },
}); 