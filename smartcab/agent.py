import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.state = {}
        self.q_table = {}
        
        self.trip_id = 0
        self.reward_by_trip = {}
        
        self.successful_trips = 0
        
        self.alpha = 0.6
        self.epsilon = 0.9
        self.gamma = 0.4
        
        self.new_state = None
    
    def printRewards(self):
        print("REWARDS")
        for i in self.reward_by_trip:
            print i, self.reward_by_trip[i]

    def reset(self, destination=None):
        self.planner.route_to(destination)
        self.trip_id+=1
        self.reward_by_trip[self.trip_id]=0
        
    def printQTable(self):
        for x in self.q_table:
            print (x, ":", self.q_table[x])

    def findMax(self, what):
        max_number = 0
        max_action = None
        
        for (state,action) in self.q_table:
            if(state==self.state and self.q_table[(state,action)] > max_number):
                max_number = self.q_table[(state,action)]
                max_action = action

        if(what=='action'):
            return max_action
        elif(what=='qval'):
            return max_number
        else:
            return None

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        
        self.state = (inputs['light'], inputs['oncoming'], inputs['left'], self.next_waypoint)
        
        if any(k[0] == self.state for k in self.q_table):
            if random.random() < self.epsilon :
                action = self.findMax('action')
            else:
                action = random.choice([None, 'forward', 'left', 'right'])
        else:
            for a in [None, 'forward', 'left', 'right']:
                self.q_table[(self.state, a)] = 1
            action = random.choice([None, 'forward', 'left', 'right'])
            self.q_table[(self.state, action)] = 1
    
        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.next_waypoint_new = self.planner.next_waypoint()
        inputs_new = self.env.sense(self)
        self.new_state = (inputs_new['light'], inputs_new['oncoming'], inputs_new['left'], self.next_waypoint_new)
        
        if (self.new_state, action) not in self.q_table:
            self.q_table[(self.new_state, action)] = 1
        
        q_hat=self.q_table[(self.new_state, action)]
            
        max_number = self.findMax('qval')
        
        if(reward==12):
            self.successful_trips+=1
    
        self.reward_by_trip[self.trip_id]=self.reward_by_trip[self.trip_id]+reward
        q_hat = q_hat + (self.alpha* (reward + ((self.gamma*max_number) - q_hat)))
        self.q_table[(self.state,action)] = q_hat
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.1, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
