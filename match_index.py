
from mp4_to_wav import load_signatures, generate_audio_sig, create_query_wav, get_best_audio

from color import read_stats, get_stats, get_best_color

from calc_shots import calc_shotlist

from search import read_shotlist, match_shotlist, read_invindex

import sys
import os

# root_dir = '/Users/C1/Classes/CSCI576/csci576_project/'
root_dir = '.'

def main():

	# folder where audio wav files and jsons (use mp4_to_wav to generate this)
	audio_folder = os.path.join(root_dir, 'audio')

	# color json 
	color_file = os.path.join(root_dir, 'colors.json')

	# shot list indexes
	shot_list_dir = os.path.join(root_dir, 'index')

	# input file path
	query_file = os.path.join(root_dir, sys.argv[1])

	# if this path doesn't exist, the code will generate a wav file to this path
	query_wav_filename = sys.argv[1].split('.')[0] + '.wav'
	query_wav_path = os.path.join(root_dir, query_wav_filename)



	
	if not os.path.isfile(query_wav_path):
		print('Creating wav file')
		create_query_wav(query_file, query_wav_path)



	# dictionaries indexed by video name, these have data for all the database videos
	print('Reading database color stats')
	colors = read_stats(color_file)
	print('Loading database audio signatures')
	audios = load_signatures(audio_folder)

	video_names = list(colors.keys())



	# input dicts, these generate stats for the input file
	print('Getting color stats')
	color_input_dict = get_stats(query_file)
	print('Generating audio signature')
	audio_input_dict = generate_audio_sig(query_wav_path)
	print('Finding shot boundaries')
	input_shot_list = calc_shotlist(query_file)



	# get shotlists for each video in video_names
	# returns dictionary with video name key, possible locations as value
	print('Matching shot lists')
	possible_locs, possible_vids = match_multiple_shotlists(input_shot_list, shot_list_dir, videos=video_names)
	# print(possible_locs)
	# print(possible_vids)

	# if shot boundary doesn't find any possible locs, check everything in the next step
	if (len(possible_vids) == 0):
		possible_vids = video_names


	# get the k best results using color, each as a list of 5 video names, start frames, errors, where the same index corresponds to the same value
	# for example, top_k_color_video_names[i] is best video, with best start frame top_k_color_start_frames[i] and error top_k_color_errors[i]
	# note these lists aren't sorted by error, so the 0th index might not necessarily be the best error video
	# only searches videos specified in video_names list
	# step_size is the jump size when sliding the query video across the database videos
	top_k_color_video_names, top_k_color_start_frames, top_k_color_errors = get_best_color(color_input_dict, colors, k=10, step_size=100, video_locs=possible_locs)
	
	print(top_k_color_video_names)
	print(top_k_color_start_frames)
	print(top_k_color_errors)
	
	
	top_vids = list(set(top_k_color_video_names))
	print(top_vids)
	top_locs = {}
	for video in top_vids:
		top_locs[video] = possible_locs[video]
	print(top_locs)
	# same as above for audio
	# only searches videos specified in video_names list
	top_k_audio_video_names, top_k_audio_start_frames, top_k_audio_errors = get_best_audio(audio_input_dict, audios, k=1, video_locs=top_locs)

	print(top_k_audio_video_names)
	print(top_k_audio_start_frames)
	print(top_k_audio_errors)


	best_video = top_k_audio_video_names[0]
	# add 2 to best frame to fix the mapping from video frame to audio frame
	best_frame = top_k_audio_start_frames[0] + 2

	print("Best video: " + best_video)
	print("Best start frame: " + str(best_frame))



def match_multiple_shotlists(input_shot_list,shot_list_dir, videos=[]):

	outputs = {}
	possible_vids = []

	for video in videos:
		# print("Checking shot list for " + video)
		shot_list_path = os.path.join(shot_list_dir, video + "_list.csv")
		inv_index_path = os.path.join(shot_list_dir, video + "_ind.txt")

		src_shot_list = read_shotlist(shot_list_path)
		inv_index = read_invindex(inv_index_path)
		possible_locs = match_shotlist(src_shot_list, input_shot_list, inv_index)

		# print(possible_locs)

		if (len(possible_locs) != 0):
			possible_vids.append(video)

		outputs[video] = possible_locs

	return outputs, possible_vids




if __name__ == '__main__':
	main()