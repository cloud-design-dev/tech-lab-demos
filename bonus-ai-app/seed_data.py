#!/usr/bin/env python3

"""
Seed data for the Cat Facts AI application
Contains interesting and educational cat facts for immediate user interaction
"""

from datetime import datetime

# Comprehensive collection of cat facts organized by category
CAT_FACTS_SEED_DATA = [
    # Behavior Facts
    {
        "fact": "Cats spend 70% of their lives sleeping, which equals 13-16 hours a day. This helps them conserve energy for hunting, even though domestic cats don't need to hunt for survival.",
        "query": "behavior",
        "category": "behavior"
    },
    {
        "fact": "When cats purr, it's not just a sign of contentment. Purring frequencies between 20-50 Hz can promote bone healing and reduce pain and swelling in cats.",
        "query": "behavior",
        "category": "behavior"
    },
    {
        "fact": "Cats have a third eyelid called a nictitating membrane that helps protect their eyes during fights or while hunting through tall grass.",
        "query": "behavior",
        "category": "anatomy"
    },
    {
        "fact": "A cat's tail is an extension of their spine and contains 19-23 vertebrae. Cats use their tails for balance and communication, with different positions indicating different moods.",
        "query": "behavior",
        "category": "anatomy"
    },
    {
        "fact": "Cats can rotate their ears 180 degrees and have 32 muscles controlling each ear, compared to humans who have only 6 ear muscles.",
        "query": "behavior",
        "category": "anatomy"
    },
    
    # Hunting & Senses
    {
        "fact": "Cats have excellent night vision and can see in light levels six times lower than what humans need. Their eyes reflect light, which is why they appear to glow in the dark.",
        "query": "hunting",
        "category": "senses"
    },
    {
        "fact": "A cat's whiskers are roughly as wide as their body, helping them determine if they can fit through tight spaces. Whiskers also detect air currents and vibrations.",
        "query": "hunting",
        "category": "senses"
    },
    {
        "fact": "Cats can hear frequencies up to 64,000 Hz (humans can only hear up to 20,000 Hz), which helps them detect the high-pitched sounds made by small prey like mice.",
        "query": "hunting",
        "category": "senses"
    },
    {
        "fact": "Cats have a success rate of only 10% when hunting birds, but up to 60% when hunting small mammals like mice and voles.",
        "query": "hunting",
        "category": "hunting"
    },
    {
        "fact": "Cats' retractable claws stay sharp because they're only extended when needed. The outer sheaths shed regularly, revealing new sharp claws underneath.",
        "query": "hunting",
        "category": "anatomy"
    },
    
    # Communication
    {
        "fact": "Adult cats rarely meow to communicate with other cats - they primarily meow to communicate with humans. Cats developed this behavior to mimic human baby cries.",
        "query": "communication",
        "category": "communication"
    },
    {
        "fact": "Cats have over 100 different vocal sounds, while dogs only have about 10. Each cat develops a unique 'vocabulary' to communicate with their human family.",
        "query": "communication",
        "category": "communication"
    },
    {
        "fact": "When cats slowly blink at you, it's called a 'cat kiss' and indicates trust and affection. You can return the gesture by slowly blinking back at them.",
        "query": "communication",
        "category": "communication"
    },
    {
        "fact": "Cats mark their territory through scent glands located in their cheeks, forehead, paws, and tail base. When they rub against you, they're marking you as 'theirs.'",
        "query": "communication",
        "category": "communication"
    },
    
    # Physical Abilities
    {
        "fact": "Cats can run up to 30 mph (48 km/h) in short bursts and can jump up to 6 times their body length horizontally and 3 times their height vertically.",
        "query": "physical",
        "category": "abilities"
    },
    {
        "fact": "Cats always land on their feet due to their 'righting reflex.' They can twist their flexible spine and use their tail as a rudder to orient themselves during a fall.",
        "query": "physical",
        "category": "abilities"
    },
    {
        "fact": "A cat's flexible spine has 30 vertebrae (humans have 24), giving them incredible flexibility and allowing them to squeeze through any opening larger than their skull.",
        "query": "physical",
        "category": "anatomy"
    },
    {
        "fact": "Cats walk like camels and giraffes - they move both right feet first, then both left feet. This gait helps them move silently when stalking prey.",
        "query": "physical",
        "category": "abilities"
    },
    
    # History & Evolution
    {
        "fact": "Cats were first domesticated around 9,000 years ago in the Near East, likely attracted to human settlements by the abundance of rodents in grain stores.",
        "query": "history",
        "category": "history"
    },
    {
        "fact": "Ancient Egyptians worshipped cats and believed they were sacred. Killing a cat, even accidentally, was punishable by death in ancient Egypt.",
        "query": "history",
        "category": "history"
    },
    {
        "fact": "The ancestor of all domestic cats is the African wildcat (Felis lybica), which still exists today and looks remarkably similar to modern tabby cats.",
        "query": "history",
        "category": "evolution"
    },
    {
        "fact": "Cats have been aboard ships for centuries to control rodent populations. They played a crucial role in protecting food supplies during long ocean voyages.",
        "query": "history",
        "category": "history"
    },
    
    # Unique Facts
    {
        "fact": "Cats have a unique collarbone that floats freely, allowing them to squeeze through any space their head can fit through. This is why they're such excellent escape artists.",
        "query": "anatomy",
        "category": "anatomy"
    },
    {
        "fact": "A group of cats is called a 'clowder,' a male cat is a 'tom,' a female cat is a 'molly' or 'queen,' and baby cats are 'kittens' until they're about one year old.",
        "query": "general",
        "category": "terminology"
    },
    {
        "fact": "Cats have individual nose prints, just like human fingerprints. No two cats have identical nose prints, making each cat's nose pattern unique.",
        "query": "anatomy",
        "category": "anatomy"
    },
    {
        "fact": "Indoor cats typically live 13-17 years, while outdoor cats average only 2-5 years due to dangers like traffic, predators, and disease.",
        "query": "health",
        "category": "health"
    },
    {
        "fact": "Cats can get sunburned, especially white cats and those with light-colored fur. Their ear tips and noses are particularly vulnerable to UV damage.",
        "query": "health",
        "category": "health"
    },
    {
        "fact": "The oldest known cat lived to be 38 years old. Crème Puff, a cat from Texas, lived from 1967 to 2005, which is equivalent to about 168 human years.",
        "query": "records",
        "category": "records"
    },
    {
        "fact": "Cats cannot taste sweetness due to a genetic mutation that deactivated their sweet taste receptors. This is why cats show no interest in sugary foods.",
        "query": "senses",
        "category": "senses"
    },
    {
        "fact": "A cat's brain is 90% similar to a human brain. Both humans and cats have identical regions in their brains that are responsible for emotions.",
        "query": "intelligence",
        "category": "anatomy"
    },
    {
        "fact": "Cats have scent glands between their toes, which is why they scratch things. They're not just sharpening their claws - they're also marking their territory with scent.",
        "query": "behavior",
        "category": "behavior"
    },
    {
        "fact": "The richest cat in the world inherited $13 million from its owner. Blackie, a British cat, was left the fortune when his owner died in 1988.",
        "query": "records",
        "category": "records"
    },
    {
        "fact": "Cats can be allergic to humans, just like humans can be allergic to cats. They can develop allergies to human dander, perfumes, and cleaning products.",
        "query": "health",
        "category": "health"
    },
    {
        "fact": "Cats sweat only through their paw pads. When they're hot or stressed, you might notice wet paw prints on smooth surfaces like veterinary exam tables.",
        "query": "anatomy",
        "category": "anatomy"
    },
    {
        "fact": "The term 'cat's pajamas' became popular in the 1920s and means something wonderful or remarkable. It was part of a trend of using animal-related phrases to describe excellence.",
        "query": "culture",
        "category": "culture"
    },
    {
        "fact": "Cats typically have 18 toes - 5 on each front paw and 4 on each back paw. However, polydactyl cats can have up to 28 toes total due to a genetic trait.",
        "query": "anatomy",
        "category": "anatomy"
    },
    {
        "fact": "A cat's learning ability is comparable to that of a 2-3 year old child. They can learn by observation and can be trained to respond to their names and simple commands.",
        "query": "intelligence",
        "category": "intelligence"
    },
    {
        "fact": "Cats have a special scent organ called the Jacobson's organ (vomeronasal organ) located in the roof of their mouth, which helps them analyze chemical information from their environment.",
        "query": "senses",
        "category": "senses"
    },
    {
        "fact": "The 'flehmen response' - when cats open their mouths and curl back their lips after smelling something - helps direct scents to their Jacobson's organ for better analysis.",
        "query": "behavior",
        "category": "behavior"
    },
    {
        "fact": "Cats prefer their water bowl to be away from their food bowl. In the wild, cats instinctively know that water near a kill site might be contaminated.",
        "query": "behavior",
        "category": "behavior"
    },
    {
        "fact": "The world's smallest cat breed is the Singapura, weighing only 4-8 pounds when fully grown. They originated in Singapore and are known for their large eyes and small stature.",
        "query": "breeds",
        "category": "breeds"
    },
    {
        "fact": "Maine Coon cats are the largest domestic cat breed, with males weighing up to 25 pounds. Despite their size, they're known for their gentle, dog-like personalities.",
        "query": "breeds",
        "category": "breeds"
    },
    {
        "fact": "Cats have been in space! In 1963, France sent a cat named Félicette into space. She survived the trip and returned safely to Earth, contributing to space research.",
        "query": "history",
        "category": "history"
    },
    {
        "fact": "A cat's whiskers will regrow if cut or damaged, but they should never be trimmed as they're essential sensory tools for navigation and spatial awareness.",
        "query": "anatomy",
        "category": "anatomy"
    },
    {
        "fact": "Cats can dream during REM sleep, just like humans. Research suggests they likely dream about familiar activities like hunting, playing, or interacting with their owners.",
        "query": "sleep",
        "category": "behavior"
    }
]

def get_seed_facts():
    """
    Returns formatted seed data with timestamps and metadata
    """
    seed_facts = []
    base_time = datetime.utcnow()
    
    for i, fact_data in enumerate(CAT_FACTS_SEED_DATA):
        # Create slightly different timestamps for each fact
        fact_time = base_time.replace(microsecond=i * 1000)
        
        seed_facts.append({
            "fact": fact_data["fact"],
            "metadata": {
                "query": fact_data["query"],
                "category": fact_data["category"],
                "timestamp": fact_time.isoformat(),
                "model": "pre-seeded",
                "source": "educational_database"
            }
        })
    
    return seed_facts

def get_random_facts(count=5):
    """Get a random selection of facts"""
    import random
    facts = get_seed_facts()
    return random.sample(facts, min(count, len(facts)))

def get_facts_by_category(category):
    """Get all facts for a specific category"""
    return [
        {
            "fact": fact["fact"],
            "metadata": fact["metadata"]
        }
        for fact in get_seed_facts() 
        if fact["metadata"]["category"] == category
    ]

def get_available_categories():
    """Get list of available categories"""
    categories = set()
    for fact in CAT_FACTS_SEED_DATA:
        categories.add(fact["category"])
    return sorted(list(categories))

# Category descriptions for the UI
CATEGORY_DESCRIPTIONS = {
    "behavior": "How cats act and behave in different situations",
    "anatomy": "Physical structure and body parts of cats",
    "senses": "Cat sensory abilities and perception",
    "hunting": "Hunting skills and predatory behaviors",
    "communication": "How cats communicate with humans and other cats",
    "abilities": "Physical capabilities and skills",
    "history": "Historical facts about cats and humans",
    "evolution": "How cats evolved and developed",
    "health": "Health-related facts and care information",
    "intelligence": "Cognitive abilities and learning capacity",
    "breeds": "Information about different cat breeds",
    "culture": "Cultural references and social aspects",
    "records": "Record-breaking cats and achievements",
    "sleep": "Sleep patterns and dream behaviors",
    "terminology": "Names and terms related to cats"
}