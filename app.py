# Save simulation result
simulation_id = storage.save_simulation(
    context_id,
    interaction_type,
    entity_ids,
    current_interaction,
    metadata,
    current_turn_number
)

logger.info(f"Created unified simulation: {simulation_id} ({interaction_type}, {len(entities)} entities)")

@app.route('/api/unified-simulations/<simulation_id>/continue', methods=['POST'])
@handle_exceptions
def continue_unified_simulation(simulation_id):
    """
    Continue an existing simulation with additional turns.
    
    Request body:
        n_turns: Number of turns to generate (default: 1)
        simulation_rounds: Number of LLM calls to make (default: 1)
        
    Returns:
        JSON response with the updated simulation
    """
    # Get the existing simulation
    simulation = storage.get_simulation(simulation_id)
    
    if not simulation:
        return error_response(f"Simulation with ID {simulation_id} not found", 404)
    
    # Get the request data
    data = request.json or {}
    n_turns = data.get('n_turns', 1)
    simulation_rounds = data.get('simulation_rounds', 1)
    
    # Validate parameters
    try:
        n_turns = int(n_turns)
        simulation_rounds = int(simulation_rounds)
        if n_turns <= 0 or simulation_rounds <= 0:
            return error_response("n_turns and simulation_rounds must be positive integers")
    except ValueError:
        return error_response("n_turns and simulation_rounds must be valid integers")
    
    # Get the context
    context = storage.get_context(simulation['context_id'])
    if not context:
        return error_response(f"Context with ID {simulation['context_id']} not found", 404)
    
    # Get the entities
    entities = []
    for entity_id in simulation['entity_ids']:
        entity = storage.get_entity(entity_id)
        if not entity:
            return error_response(f"Entity with ID {entity_id} not found", 404)
        entities.append(entity)
    
    # Check if LLM is configured
    if not lm:
        return error_response("LLM is not configured", 503)
    
    # Initialize simulator
    simulator = InteractionSimulator()
    
    # Extract the last turn number from the content
    last_turn_number = 0
    try:
        # Look for the last "TURN X" or similar in the result
        lines = simulation['content'].splitlines()
        for line in reversed(lines):
            if "TURN" in line or "Turn" in line or "turn" in line:
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        last_turn_number = int(part)
                        break
                if last_turn_number > 0:
                    break
    except Exception as e:
        logger.warning(f"Failed to extract last turn number: {str(e)}")
        # Default to 0 if we can't determine the last turn number
    
    # Run the simulation for the requested number of rounds
    current_interaction = simulation['content']
    current_turn_number = last_turn_number
    
    for round_num in range(simulation_rounds):
        logger.info(f"Running simulation continuation round {round_num + 1}/{simulation_rounds}")
        
        # Execute the simulation
        prediction = simulator.forward(
            entities=entities,
            context=context['description'],
            n_turns=n_turns,
            last_turn_number=current_turn_number,
            previous_interaction=current_interaction
        )
        
        # Update for next round
        current_interaction = current_interaction + "\n\n" + prediction.content
        current_turn_number = prediction.final_turn_number
    
    # Update the simulation in storage
    updated_simulation = storage.update_simulation(
        simulation_id,
        current_interaction,
        {**simulation.get('metadata', {}), 'last_continued_at': datetime.datetime.now().isoformat()},
        current_turn_number
    )
    
    return success_response({
        "id": simulation_id,
        "context_id": simulation['context_id'],
        "result": current_interaction,
        "interaction_type": simulation['interaction_type'],
        "entity_count": len(entities),
        "final_turn_number": current_turn_number
    }) 