import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    corpus_len = len(corpus.keys())
    page_len = len(corpus[page])
    prob_dist = {} # probability distribution
    
    # If page has no outgoing links, then transition_model should return a probability
    # distribution that chooses randomly among all pages with equal probability.
    # (In other words, if a page has no links, we can pretend it has links to all pages in the corpus, including itself.)
    if page_len == 0:
        for p in corpus:
            prob_dist[p] = 1 / corpus_len
        return prob_dist

    # With prob damping_factor, randomly choose a links from page with equal probability
    prob_from_page = damping_factor / page_len
    # With prob 1 - damping_factor, randomly choose a links from all pages with equal probability
    prob_from_all = (1 - damping_factor) / corpus_len

    for key in corpus.keys():
        if key in corpus[page]:
            prob_dist[key] = prob_from_page + prob_from_all
        else:
            prob_dist[key] = prob_from_all

    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initialize a dictionary to keep track of how many times a page has been sampled
    sample_dict = corpus.copy()
    for i in sample_dict.keys():
        sample_dict[i] = 0

    # Initialize the init sampled page
    sample = random.choice(list(corpus.keys()))
    sample_dict[sample] += 1

    for _ in range(n):
        dist = transition_model(corpus, sample, damping_factor)
        dist_list = list(dist.keys())
        dist_weights = [dist[i] for i in dist_list]

        sample = random.choices(dist_list, weights=dist_weights, k=1)[0]
        sample_dict[sample] += 1

    # Normalize the sample_dict
    for i in sample_dict.keys():
        sample_dict[i] /= n

    return sample_dict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize constants
    corpus_len = len(corpus.keys())
    init_rank = 1 / corpus_len

    # Initialize the ranks dictionary
    ranks = {page: init_rank for page in corpus} # probability distribution

    # Repeat until no change larger than 0.001
    max_change = init_rank
    while max_change > 0.001:
        # Reset max_change
        max_change = 0
        for page in corpus:
            # Calculate the sum of the PageRank of every page that links to the given page
            sum_pr = 0
            for linked_page in corpus:
                if page in corpus[linked_page]:
                    sum_pr += ranks[linked_page] / len(corpus[linked_page])
                # A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself)
                if len(corpus[linked_page]) == 0:
                    sum_pr += ranks[linked_page] / corpus_len
            # Calculate the new PageRank based on the algorithm: PR(p) = (1 - d) / N + d * sum(PR(i) / NumLinks(i))
            page_rank = (1 - damping_factor) / corpus_len + damping_factor * sum_pr
            # Calculate the change in PageRank for all pages
            max_change = max(max_change, abs(page_rank - ranks[page]))
            # Update the ranks dictionary
            ranks[page] = page_rank

    return ranks


if __name__ == "__main__":
    main()
