[
    "Sentence 1", #0
    "Sentence 2", #1
    "Sentence 3", #2
    "Sentence 4", #3
    "Sentence 5", #4
    "Sentence 6", #5
    "Sentence 7", #6
    "Sentence 8", #7
    "Sentence 9", #8
    "Sentence 10", #9
    "Sentence 11", #10
    "Sentence 12", #11
]

Config(max_size=5, overlap=2)

Chunk 1: ["Sentence 1", "Sentence 2", "Sentence 3", "Sentence 4", "Sentence 5"] -> #4
Chunk 2: ["Sentence 4", "Sentence 5", "Sentence 6", "Sentence 7", "Sentence 8"] -> #7
Chunk 3: ["Sentence 7", "Sentence 8", "Sentence 9", "Sentence 10", "Sentence 11"] -> 10
Chunk 4: ["Sentence 10", "Sentence 11", "Sentence 12"] -> 11