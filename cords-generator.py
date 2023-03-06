import mido
import music21 as music
import random
import math

INPUT_FILE = "input3.mid"
OUTPUT_FILE = "output.mid"

class Note:
    """ Class reprsent the note, has midi number, duration interval and name. """

    def __init__(self, name, midi_n : int, duration : "tuple(float, float)") -> None:
        self.name = name
        self.midi_n = midi_n
        self.duration = duration

    def __str__(self) -> str:
        return f"Note {self.name} {self.duration}, {self.midi_n}"
    
    def get_chords(self, is_minor: bool):
        """ get all possible chords with this note as root note. """
        chords = []
        if is_minor:
            chords.append(Chord(0, self, True))
            chords.append(Chord(0, self, True, 1))
            chords.append(Chord(0, self, True, 2))
        else:
            chords.append(Chord(0, self, False))
            chords.append(Chord(0, self, False, 1))
            chords.append(Chord(0, self, False, 2))
        return chords
    
    
    
    def print_Chords(self):
        for chord in self.get_chords():
            print(chord)


class Chord:
    """ Class repsents the chord that constructed according to root note, inverse type and scale. """

    def __init__(self, weight : int, root_note : Note, minor : bool = False, inverse : int = 0) -> None:
        self.weight = weight
        self.minor = minor
        self.inverse = inverse
        root_n = root_note.midi_n
        if minor:
            if inverse == 0:
                self.notes = (root_n, root_n + 3, root_n + 7)
            elif inverse == 1:
                self.notes = (root_n + 12, root_n + 3, root_n + 7)
            elif inverse == 2:
                self.notes = (root_n + 12, root_n + 15, root_n + 7)
        if not minor:
            if inverse == 0:
                self.notes = (root_n, root_n + 4, root_n + 7)
            elif inverse == 1:
                self.notes = (root_n + 12, root_n + 4, root_n + 7)
            elif inverse == 2:
                self.notes = (root_n + 12, root_n + 16, root_n + 7)
    
    def __str__(self) -> str:
        return f"{str(self.notes)}, minor = {self.minor}, inverse = {self.inverse}, weight = {self.weight}"

    def __hash__(self) -> int:
        return hash(str(self.notes))

    def __eq__(self, __o: object) -> bool:
        return self.notes == self.notes


def open_file()-> mido.MidiFile:
    """ Open midi file. """
    my_midi = mido.MidiFile(INPUT_FILE,clip=True)
    return my_midi

def get_PitchedTimespans(time_spans : "list[music.tree.spans.Timespan]") -> \
    "list[music.tree.spans.PitchedTimespan]":
    """ Helper function to parse notes from midi file. """
    pitched = []
    for t_span in time_spans:
        if type(t_span) is music.tree.spans.PitchedTimespan:
            pitched.append(t_span)
    return pitched

def get_notes(pitched : "list[music.tree.spans.PitchedTimespan]") -> "list[Note]":
    """ Get list of notes as Note objects from midi file. """
    notes : list[Note] = []
    current_offset = 0
    for pitch_time_span in pitched:
        if pitch_time_span.offset != current_offset:
            pause = Note("pause", -1, (current_offset, pitch_time_span.offset))
            notes.append(pause)
        note = Note(pitch_time_span.pitches[0].name, pitch_time_span.pitches[0].midi, (pitch_time_span.offset, pitch_time_span.endTime))
        notes.append(note)
        current_offset = pitch_time_span.endTime
    return notes

def print_notes(notes):
    """ print list of Note objects. """
    for note in notes:
        print(note)

def print_chords(chords):
    """ print list of Chord objects """
    for chord in chords:
        print(chord)

def get_harmonic_chords(tonic : int, scale, decr : int):
    """ get applicable chords wrt to key of melody (according to tables from assignment description) """

    chord_tonic = tonic - 12*decr
    print(f"tonic for chords: {chord_tonic}")
    chords = []
    root_notes = []
    is_minor = False
    if scale == "minor":
        is_minor = True
        root_notes.append(Note(None, chord_tonic, None))
        root_notes.append(Note(None, chord_tonic + 3, None))
        root_notes.append(Note(None, chord_tonic + 5, None))
        root_notes.append(Note(None, chord_tonic + 7, None))
        root_notes.append(Note(None, chord_tonic + 8, None))
        root_notes.append(Note(None, chord_tonic + 10, None))
    else:
        root_notes.append(Note(None, chord_tonic, None))
        root_notes.append(Note(None, chord_tonic + 2, None))
        root_notes.append(Note(None, chord_tonic + 4, None))
        root_notes.append(Note(None, chord_tonic + 5, None))
        root_notes.append(Note(None, chord_tonic + 7, None))
        root_notes.append(Note(None, chord_tonic + 9, None))
    for i in range (0,len(root_notes)):
        if is_minor and i in (0, 2, 3):
            chords += root_notes[i].get_chords(True)
        elif is_minor and i in (1, 4, 5):
            chords += root_notes[i].get_chords(False)
        elif not is_minor and i in (0, 3, 4):
            chords += root_notes[i].get_chords(False)
        elif not is_minor and i in (1, 2, 5):
            chords += root_notes[i].get_chords(True)
    return chords

def get_rand_accomp(chords, notes):
    """
        Construct random accompaniment of applicable chords for the melody.
        Accompaniment is a dictinoray in format (index, Chord obj) = [Note objs].
    """
    end_time = math.ceil(notes[len(notes) - 1].duration[1])
    accompaniment = {}
    ind = 0
    for i in range(0, end_time, 2):
        sub_notes = list(filter(lambda x: i<= x.duration[0] < i + 2, notes))
        accompaniment[(ind, random.choice(chords))] = sub_notes
        ind += 1
    return accompaniment

def print_accomp(accomp : dict):
    for key in accomp.keys():
        print(key[0], key[1])
        print_notes(accomp[key])
        print("###############")
        pass

def write(file : mido.MidiFile, accomp):
    """ Create an output file that combine given melody and generated accompaniment. """
    output = mido.MidiFile()
    output.ticks_per_beat = file.ticks_per_beat
    output.tracks += [file.tracks[0], file.tracks[1]]
    my_track = mido.MidiTrack()
    my_track.append(file.tracks[1][0])
    for chord in accomp.keys():
        chord_notes = chord[1].notes
        for j in range(0,2):
            for i in [0, 1, 2]:
                my_track.append(mido.Message("note_on", channel = 0, note = chord_notes[i], velocity = 50, time = 0))
            my_track.append(mido.Message("note_off", channel = 0, note = chord_notes[0], velocity = 0, time = 384))
            for i in [1, 2]:
                my_track.append(mido.Message("note_off", channel = 0, note = chord_notes[i], velocity = 0, time = 0))
    my_track.append(file.tracks[1][len(file.tracks[1]) - 1])
    output.tracks.append(my_track)
    output.save(OUTPUT_FILE)

def estimate_chord(chord : Chord, notes, is_minor):
    """ 
        Update score of the Chord. 
        Increase the Chord's weight if it is not to close to notes in quater,
        consits of some notes from quater
        and has an appropriate scale.
    """

    contain_note = 2
    not_so_close = 2
    ok_minor = 0
    ok_major = 0
    if is_minor:
        ok_minor = 1
    else:
        ok_major = 1
    if len(notes) != 0:
        for note in notes:
            if note.midi_n % 12 in [ x % 12 for x in chord.notes]:
                chord.weight += contain_note
        if max(chord.notes) < min([note.midi_n for note in notes]) - 8:
            chord.weight += not_so_close
    if chord.minor:
        chord.weight += ok_minor
    else:
        chord.weight += ok_major

def fitness(population, is_minor):
    """ Claculate score for every accompaniment in generarion. """

    for creature in population:
        for key in creature.keys():
            estimate_chord(key[1], creature[key], is_minor)

def get_creature_score(creature):
    """ Get score for accompaniment. """
    score = 0
    for key in creature.keys():
        score += key[1].weight
    return score

def get_population_score(population):
    """ Get score for a population. """
    score = 0
    for creature in population:
        score += get_creature_score(creature)
    return score

def get_best_ind(population):
    """ Get index of accompaniment with highest score in the population. """

    max_score = -1
    max_ind = 0
    ind = 0
    for creature in population:
        creature_score = get_creature_score(creature)
        if max_score < creature_score:
            max_score = creature_score
            max_ind = ind
        ind += 1
    return max_ind

def get_worst_chord(accomp):
    """ Get index of accompaniment with lowest score in the population. """

    chord = None
    min_weight = 10000000
    for key in accomp:
        if key[1].weight < min_weight:
            min_weight = key[1].weight
            chord = key
    return chord


def crossover(creature1 : dict, creature2 : dict, given_range):
    """ 
        Two point crossover function for genetic algorithm.
        Create two new accompaniments from given two. 
    """

    point1 = random.randrange(0, given_range)
    point2  = random.randrange(0, given_range)
    while point1 == point2:
        point1 = random.randrange(given_range)
        point2  = random.randrange(given_range)
    new_creature1_list = list(creature2.items())[0:point1] + list(creature1.items())[point1 : point2] + list(creature2.items())[point2 : given_range]
    new_creature2_list = list(creature1.items())[0:point1] + list(creature2.items())[point1 : point2] + list(creature1.items())[point2 : given_range]
    new_creature1_dict = {}
    new_creature2_dict = {}
    for el1 in new_creature1_list:
        new_creature1_dict[el1[0]] = el1[1]
    for el2 in new_creature2_list:
        new_creature2_dict[el2[0]] = el2[1]
    return (new_creature1_dict, new_creature2_dict)

def mutation(population, possible_chords, is_minor):
    """ 
        Mutation function for genetic algorithm.
        Randomly change three Chords in every accompaniment in generation. 
    """

    for creature in population:
        creature_list = list(creature.items())
        for i in range (0,3):
            chord_to_mutate = random.choice(list(creature.keys()))
            saved_notes = creature.get(chord_to_mutate,None)
            new_chord = random.choice(possible_chords)
            estimate_chord(new_chord, saved_notes, is_minor)
            creature_list[chord_to_mutate[0]] = ((chord_to_mutate[0], new_chord), saved_notes)
        creature.clear()
        for el in creature_list:
            creature[el[0]] = el[1]


def genetic_algorithm(notes, chords, n_creatures, iterations, is_minor):
    """ 
        Genetic algorithm to generate accompanimnet.
        Stop criterion is the number of generarions. 
    """

    current_population = [get_rand_accomp(chords, notes) for creature in range(0,n_creatures)]
    for i in range(0,iterations):
        print(get_population_score(current_population))
        best = []
        for j in range (0, n_creatures // 2):
            ind = get_best_ind(current_population)
            best.append(current_population[ind])
            del current_population[ind]
        current_population = []
        new_generation = []
        while len(new_generation) <= n_creatures*2:
            children = crossover(random.choice(best), random.choice(best), len(best[0].keys()))
            new_generation.append(children[0])
            new_generation.append(children[1])
        mutation(new_generation, chords, is_minor)
        for j in range(0,n_creatures):
            current_population.append(new_generation[get_best_ind(new_generation)])
    return current_population[get_best_ind(current_population)]

def main():
    all_notes = []
    file = open_file()
    score = music.converter.parse(INPUT_FILE)
    is_minor = False
    key = score.analyze('key')
    time_spans : list[music.tree.spans.Timespan]= score.asTimespans()
    pitched = get_PitchedTimespans(time_spans)
    all_notes = get_notes(pitched)
    print_notes(all_notes)
    possible_chords = get_harmonic_chords(key.tonic.midi, key.mode, 1)
    possible_chords += get_harmonic_chords(key.tonic.midi, key.mode, 2)
    scale = key.mode
    if scale == "minor":
        is_minor = True
    tonic_n = key.tonic.midi
    octave = tonic_n // 12 -1
    print(scale) #scale
    print(tonic_n) # midi number of note, tonic
    print(octave) # octave
    print_chords(possible_chords)
    my_accomp = genetic_algorithm(all_notes, possible_chords, 300, 500, is_minor)
    print_accomp(my_accomp)
    write(file, my_accomp)
main()