import os
import random
import datetime

__author__ = 'tommy'



"""
Answer dict:
{
    "title" : "Answer title",
    "videoFile" : "/path/to/video.file"
}
"""
class Question(object):
    def __init__(self, database):
        print "question init"
        self.database = database
        self.correctAnswer = None
        self.answers = list()

    def getQuestion(self):
        raise Exception("Not implemented")

    def getAnswers(self):
        return self.answers

    def getCorrectAnswer(self):
        return self.correctAnswer

    def getVideoFile(self):
        return None

    def getPhotoFile(self):
        return None

    def _add_answer(self, newAnswer):
        for answer in self.answers:
            if answer['movieId'] == newAnswer['movieId']:
                return

        self.answers.append(newAnswer)

    def _get_movie_ids(self):
        movieIds = list()
        for movie in self.answers:
            movieIds.append(movie['movieId'])
        s = ','.join(map(str, movieIds))
        print "s = %s" % s
        return s

    def _get_videofile_path(self, path, filename):
        if filename[0:8] == 'stack://':
            return filename
        else:
            return os.path.join(path, filename)
        

class WhatMovieIsThisQuestion(Question):
    """
        WhatMovieIsThisQuestion
    """
    def __init__(self, database):
        Question.__init__(self, database)
        self.correctAnswer = self.database.fetchone('SELECT mv.idMovie AS movieId, mv.c00 AS title, mv.c14 AS genre, mv.strPath AS path, mv.strFilename AS filename, slm.idSet AS setId '
            + 'FROM movieview mv LEFT JOIN setlinkmovie slm ON mv.idMovie = slm.idMovie ORDER BY random() LIMIT 1')
        self._add_answer(self.correctAnswer)


        # Find other movies in set
        otherMoviesInSet = self.database.fetchall('SELECT DISTINCT mv.idMovie AS movieId, mv.c00 AS title, mv.c14 AS genre, mv.strPath AS path, mv.strFilename AS filename '
            + 'FROM movieview mv LEFT JOIN setlinkmovie slm ON mv.idMovie = slm.idMovie '
            + 'WHERE slm.idSet = ? AND mv.idMovie != ? ORDER BY random() LIMIT 3', (self.correctAnswer['setId'], self.correctAnswer['movieId']))
        for movie in otherMoviesInSet:
            self._add_answer(movie)

        # Find other movies in genre
        if len(self.answers) < 4:
            otherMoviesInGenre = self.database.fetchall('SELECT DISTINCT mv.idMovie AS movieId, mv.c00 AS title, mv.c14 AS genre, mv.strPath AS path, mv.strFilename AS filename '
                + 'FROM movieview mv WHERE genre = ? AND mv.idMovie NOT IN (?) ORDER BY random() LIMIT ?',
                                                        (self.correctAnswer['genre'], self._get_movie_ids(), 4 - len(self.answers)))
            for movie in otherMoviesInGenre:
                self._add_answer(movie)

        # Fill with random movies
        if len(self.answers) < 4:
            theRest = self.database.fetchall('SELECT DISTINCT mv.idMovie AS movieId, mv.c00 AS title, mv.c14 AS genre, mv.strPath AS path, mv.strFilename AS filename '
                + 'FROM movieview mv WHERE mv.idMovie NOT IN (?) '
                + 'ORDER BY random() LIMIT ?', (self._get_movie_ids(), 4 - len(self.answers)))
            for movie in theRest:
                self._add_answer(movie)

        print self.answers

        for answer in self.answers:
            answer['videoFile'] = self._get_videofile_path(answer['path'], answer['filename'])

        random.shuffle(self.answers)


    def getQuestion(self):
        return "What movie is this?"

    def getVideoFile(self):
        return self.correctAnswer['videoFile']


class ActorNotInMovieQuestion(Question):
    """
        ActorNotInMovieQuestion
    """
    def __init__(self, database):
        Question.__init__(self, database)
        self.actor = self.database.fetchone('SELECT a.idActor AS actorId, a.strActor AS name, a.strThumb AS thumb '
            + 'FROM movieview mv, actorlinkmovie alm, actors a '
            + 'WHERE mv.idMovie = alm.idMovie AND alm.idActor = a.idActor '
            + 'GROUP BY alm.idActor HAVING count(mv.idMovie) > 3 ORDER BY random() LIMIT 1')
        
        # Movie actor is not in
        self.correctAnswer = self.database.fetchone('SELECT mv.idMovie AS movieId, mv.c00 AS title, mv.c14 AS genre, mv.strPath AS path, mv.strFilename AS filename '
            + 'FROM movieview mv, actorlinkmovie alm '
            + 'WHERE mv.idMovie = alm.idMovie AND alm.idActor != %s ORDER BY random() LIMIT 1' % self.actor['actorId'])
        self._add_answer(self.correctAnswer)

        # Movie actor is in
        movies = self.database.fetchall('SELECT mv.idMovie AS movieId, mv.c00 AS title, mv.c14 AS genre, mv.strPath AS path, mv.strFilename AS filename '
            + 'FROM movieview mv, actorlinkmovie alm '
            + 'WHERE mv.idMovie = alm.idMovie AND alm.idActor = %s ORDER BY random() LIMIT 3' % self.actor['actorId'])
        for movie in movies:
            self._add_answer(movie)

        print self.answers

        for answer in self.answers:
            answer['videoFile'] = os.path.join(answer['path'], answer['filename'])

        random.shuffle(self.answers)


    def getQuestion(self):
        return "What movie is %s not in?" % self.actor['name']

    def getPhotoFile(self):
        if self.actor['thumb'] != '':
            return self.actor['thumb'][7:-8] # remove <thumb> and </thumb>
        else:
            return None


class WhatYearWasMovieReleasedQuestion(Question):
    """
        ActorNotInMovieQuestion
    """
    def __init__(self, database):
        Question.__init__(self, database)
        self.movie = self.database.fetchone('SELECT mv.c00 AS title, mv.c07 AS year, mv.strPath AS path, mv.strFilename AS filename '
            + 'FROM movieview mv ORDER BY random() LIMIT 1')

        minYear = int(self.movie['year']) - 5
        maxYear = int(self.movie['year']) + 5

        thisYear = datetime.datetime.today().year
        if maxYear > thisYear:
            maxYear = thisYear
            minYear = thisYear - 10

        years = list()
        years.append(int(self.movie['year']))
        while len(years) < 4:
            year = random.randint(minYear, maxYear)
            if not year in years:
                years.append(year)

        list.sort(years)

        for year in years:
            answer = {
                'title' : str(year),
                'videoFile' : os.path.join(self.movie['path'], self.movie['filename'])
            }
            self.answers.append(answer)

        self.correctAnswer = self.answers[0]
        
        print self.answers
        
    def getQuestion(self):
        return "What year was %s released?" % self.movie['title']


    def getVideoFile(self):
        return self.correctAnswer['videoFile']


def getRandomQuestion():
    subclasses = Question.__subclasses__()
    return subclasses[random.randint(0, len(subclasses) - 1)]



